"""
Workflow orchestration with step-by-step progress tracking.
"""
from typing import Dict, Any, Callable, Optional
import uuid
from datetime import datetime
from app.api.schemas import WorkflowStep, WorkflowProgress
from app.api.websocket import manager
from app.emotions.emotion_redis import analyze_user
from app.agents.user_mapper import map_summary_to_fields
from app.agents.mentor import load_athena_profile, get_athena_mbti, update_athena_mbti
from app.agents.wedana import wedana_classifier, update_pain_history
from app.agents.combinator import generate_final_response
from app.agents.eval import empathy_from_pain
from app.agents.personality_picker import pick_new_personality_by_user_mbti
from app.agents.enhanced_ego_system import EnhancedEgoSystem
from app.config import config
from app.utils.logger import logger
from app.utils.error_handler import handle_error


class WorkflowOrchestrator:
    """Orchestrates the complete workflow with progress tracking."""
    
    def __init__(self):
        """Initialize workflow orchestrator."""
        self.ego_system = EnhancedEgoSystem()
        logger.debug("WorkflowOrchestrator initialized")
    
    async def process_user_interaction(
        self,
        user_id: str,
        session_id: str,
        user_input: str,
        workflow_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Process complete user interaction workflow.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            user_input: User input text
            workflow_id: Optional workflow ID for tracking
            progress_callback: Optional callback for progress updates
            
        Returns:
            Complete interaction result
        """
        if not workflow_id:
            workflow_id = str(uuid.uuid4())
        
        steps = []
        total_steps = 9
        
        try:
            # Step 1: Emotion Analysis
            await self._update_progress(
                workflow_id, 1, "emotion_analysis", "processing",
                {"message": "Analyzing user emotions..."},
                steps, progress_callback
            )
            
            user_analysis = analyze_user(user_id, session_id, user_input)
            user_pain = float(user_analysis.get("pain_level", 0))
            
            await self._update_progress(
                workflow_id, 1, "emotion_analysis", "completed",
                {
                    "emotions": user_analysis.get("emotions", {}),
                    "pain_level": user_pain,
                    "vad": user_analysis.get("emotions", {}).get("vad", {})
                },
                steps, progress_callback
            )
            
            # Step 2: User Pain Calculation
            await self._update_progress(
                workflow_id, 2, "user_pain_calculation", "processing",
                {"message": "Calculating user pain level..."},
                steps, progress_callback
            )
            
            await self._update_progress(
                workflow_id, 2, "user_pain_calculation", "completed",
                {"pain_level": user_pain},
                steps, progress_callback
            )
            
            # Step 3: MBTI Detection
            await self._update_progress(
                workflow_id, 3, "mbti_detection", "processing",
                {"message": "Detecting personality type..."},
                steps, progress_callback
            )
            
            mbti_result = user_analysis.get("mbti", {})
            
            await self._update_progress(
                workflow_id, 3, "mbti_detection", "completed",
                {"mbti": mbti_result},
                steps, progress_callback
            )
            
            # Step 4: Ego Impact Analysis
            await self._update_progress(
                workflow_id, 4, "ego_impact_analysis", "processing",
                {"message": "Analyzing ego impact..."},
                steps, progress_callback
            )
            
            ego_result = self.ego_system.process_user_input(user_input)
            
            await self._update_progress(
                workflow_id, 4, "ego_impact_analysis", "completed",
                {
                    "dimension_impacts": ego_result["pain_analysis"]["dimension_impacts"],
                    "most_affected_dimension": ego_result["pain_analysis"]["most_affected_dimension"]
                },
                steps, progress_callback
            )
            
            # Step 5: Athena Pain Calculation
            await self._update_progress(
                workflow_id, 5, "athena_pain_calculation", "processing",
                {"message": "Calculating Athena's emotional response..."},
                steps, progress_callback
            )
            
            athena_pain = ego_result["final_pain"]
            
            await self._update_progress(
                workflow_id, 5, "athena_pain_calculation", "completed",
                {
                    "pain_level": athena_pain,
                    "rule_based": ego_result["pain_analysis"]["rule_based_pain"],
                    "llm_based": ego_result["pain_analysis"].get("llm_pain"),
                    "confidence": ego_result["pain_analysis"]["confidence"]
                },
                steps, progress_callback
            )
            
            # Step 6: Empathy Metrics
            await self._update_progress(
                workflow_id, 6, "empathy_metrics", "processing",
                {"message": "Calculating empathy metrics..."},
                steps, progress_callback
            )
            
            user_summary = map_summary_to_fields(user_analysis)
            empathy_result = empathy_from_pain(athena_pain, user_pain)
            
            await self._update_progress(
                workflow_id, 6, "empathy_metrics", "completed",
                empathy_result,
                steps, progress_callback
            )
            
            # Step 7: Response Generation
            await self._update_progress(
                workflow_id, 7, "response_generation", "processing",
                {"message": "Generating empathetic response..."},
                steps, progress_callback
            )
            
            athena_profile = load_athena_profile()
            final_response = generate_final_response(
                user_summary=user_summary,
                athena_profile=athena_profile
            )
            
            # Extract response text from tags
            import re
            response_match = re.search(
                r"<final_answer>\s*(.*?)\s*</final_answer>",
                final_response,
                re.DOTALL | re.IGNORECASE
            )
            response_text = response_match.group(1).strip() if response_match else final_response
            
            await self._update_progress(
                workflow_id, 7, "response_generation", "completed",
                {"response": response_text},
                steps, progress_callback
            )
            
            # Step 8: Personality Adaptation
            await self._update_progress(
                workflow_id, 8, "personality_adaptation", "processing",
                {"message": "Checking personality compatibility..."},
                steps, progress_callback
            )
            
            mismatch = 1 - empathy_result["alignment"]
            personality_changed = False
            
            if mismatch >= config.BIG_MISMATCH_THRESHOLD:
                from app.agents.athena_personality import athena_mbti_personalities
                athena_mbti_type, athena_mbti_info = get_athena_mbti(athena_profile)
                user_mbti_type = user_summary.get("personality", {}).get("mbti", "")
                new_personality = pick_new_personality_by_user_mbti(
                    user_mbti_type,
                    athena_mbti_personalities  # Pass the full personalities list
                )
                
                if new_personality:
                    import os
                    current_dir = os.path.dirname(os.path.dirname(__file__))
                    profile_path = os.path.join(current_dir, "agents", "athena_profile.json")
                    update_athena_mbti(profile_path, new_personality)
                    personality_changed = True
            
            await self._update_progress(
                workflow_id, 8, "personality_adaptation", "completed",
                {
                    "personality_changed": personality_changed,
                    "mismatch": mismatch,
                    "threshold": config.BIG_MISMATCH_THRESHOLD
                },
                steps, progress_callback
            )
            
            # Step 9: Crisis Check
            await self._update_progress(
                workflow_id, 9, "crisis_check", "processing",
                {"message": "Checking for crisis mode..."},
                steps, progress_callback
            )
            
            crisis_mode = user_analysis.get("crisis_mode", {})
            crisis_detected = crisis_mode.get("crisis_mode", False)
            
            await self._update_progress(
                workflow_id, 9, "crisis_check", "completed",
                {
                    "crisis_detected": crisis_detected,
                    "crisis_response": user_analysis.get("crisis_response")
                },
                steps, progress_callback
            )
            
            # Update pain history
            update_pain_history(user_input, athena_pain)
            
            # Compile final result
            result = {
                "workflow_id": workflow_id,
                "user_id": user_id,
                "session_id": session_id,
                "user_input": user_input,
                "athena_response": response_text,
                "workflow_steps": steps,
                "metrics": {
                    "user_pain": user_pain,
                    "athena_pain": athena_pain,
                    "empathy_metrics": empathy_result,
                    "ego_metrics": ego_result["ego_metrics"]
                },
                "ego_state": ego_result["ego_state"],
                "crisis_mode": crisis_detected,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send completion message
            await self._send_progress_update(
                workflow_id,
                {
                    "type": "workflow_complete",
                    "workflow_id": workflow_id,
                    "result": result
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            error_step = WorkflowStep(
                step_number=len(steps) + 1,
                step_name="error",
                status="error",
                error=str(e),
                timestamp=datetime.now()
            )
            steps.append(error_step)
            
            await self._send_progress_update(
                workflow_id,
                {
                    "type": "workflow_error",
                    "workflow_id": workflow_id,
                    "error": str(e),
                    "steps": [s.dict() for s in steps]
                }
            )
            
            raise
    
    async def _update_progress(
        self,
        workflow_id: str,
        step_number: int,
        step_name: str,
        status: str,
        data: Dict[str, Any],
        steps: list,
        progress_callback: Optional[Callable] = None
    ):
        """Update workflow progress."""
        step = WorkflowStep(
            step_number=step_number,
            step_name=step_name,
            status=status,
            data=data,
            timestamp=datetime.now()
        )
        
        # Update or add step
        existing_idx = next(
            (i for i, s in enumerate(steps) if s.step_number == step_number),
            None
        )
        if existing_idx is not None:
            steps[existing_idx] = step
        else:
            steps.append(step)
        
        # Calculate progress
        progress = WorkflowProgress(
            workflow_id=workflow_id,
            current_step=step_number,
            total_steps=9,
            steps=steps,
            progress_percentage=(step_number / 9) * 100
        )
        
        # Send via WebSocket
        await self._send_progress_update(
            workflow_id,
            {
                "type": "workflow_progress",
                "progress": progress.dict()
            }
        )
        
        # Call custom callback if provided
        if progress_callback:
            try:
                progress_callback(progress)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    async def _send_progress_update(self, workflow_id: str, message: Dict[str, Any]):
        """Send progress update via WebSocket."""
        try:
            await manager.send_to_workflow(workflow_id, message)
        except Exception as e:
            logger.debug(f"Could not send progress update (no active connection): {e}")


# Global orchestrator instance
orchestrator = WorkflowOrchestrator()

