"""
Model Manager for Dreams.ai
Simple singleton for pre-loading models to avoid repeated loading times.
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from langchain_community.chat_models import ChatLlamaCpp
import torch
from diffusers import DiffusionPipeline

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Simple Model Manager for Dreams.ai
    Pre-loads models to avoid repeated loading times during pipeline execution.
    """
    
    _instance = None
    _llm = None
    _sdxl_turbo = None
    _sdxl_lora = None
    _models_loaded = False
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance of ModelManager"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def load_all_models(self):
        """Pre-load all models at startup"""
        if self._models_loaded:
            logger.info("✅ Models already loaded")
            return
        
        logger.info("🔄 Starting model pre-loading...")
        start_time = time.time()
        
        try:
            # Load LLM model
            self._load_llm()
            
            # Load image generation models
            self._load_image_models()
            
            self._models_loaded = True
            load_time = time.time() - start_time
            
            logger.info(f"✅ All models loaded successfully in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            raise
    
    def _load_llm(self):
        """Load the GGUF LLM model"""
        if self._llm is not None:
            logger.info("✅ LLM already loaded, skipping...")
            return
            
        logger.info("🔄 Loading GGUF LLM model...")
        
        # Simple environment detection
        import os
        import threading
        
        is_flask_server = threading.active_count() > 1
        optimal_threads = min(8, os.cpu_count() // 2) if is_flask_server else min(16, os.cpu_count())
        
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"))
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"LLM model file not found: {model_path}")
        
        # GPU layer allocation
        gpu_layers = 35 if torch.cuda.is_available() else 0
        
        self._llm = ChatLlamaCpp(
            model_path=model_path,
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9,
            verbose=True,
            n_ctx=2048,
            n_threads=optimal_threads,
            n_batch=512,
            use_mmap=True,
            use_mlock=False,
            f16_kv=True,
            n_gpu_layers=gpu_layers,
        )
        
        logger.info("✅ GGUF LLM model loaded successfully")
    
    def _load_image_models(self):
        """Load image generation models"""
        logger.info("🔄 Loading image generation models...")
        
        # Load SDXL Turbo
        if self._sdxl_turbo is None:
            logger.info("🔄 Loading SDXL Turbo pipeline...")
            try:
                self._sdxl_turbo = DiffusionPipeline.from_pretrained(
                    "stabilityai/sdxl-turbo",
                    torch_dtype=torch.float16,
                    variant="fp16"
                )
                
                if torch.cuda.is_available():
                    self._sdxl_turbo = self._sdxl_turbo.to("cuda")
                    logger.info(f"✅ SDXL Turbo loaded on GPU: {torch.cuda.get_device_name()}")
                else:
                    logger.info("⚠️ CUDA not available, SDXL Turbo using CPU")
            except Exception as e:
                logger.error(f"❌ Failed to load SDXL Turbo: {e}")
                self._sdxl_turbo = None
        
        # Load SDXL LoRA
        if self._sdxl_lora is None:
            logger.info("🔄 Loading SDXL LoRA pipeline...")
            try:
                self._sdxl_lora = DiffusionPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-xl-base-1.0",
                    torch_dtype=torch.float16,
                    variant="fp16"
                )
                
                if torch.cuda.is_available():
                    self._sdxl_lora = self._sdxl_lora.to("cuda")
                    logger.info(f"✅ SDXL LoRA loaded on GPU: {torch.cuda.get_device_name()}")
                else:
                    logger.info("⚠️ CUDA not available, SDXL LoRA using CPU")
            except Exception as e:
                logger.error(f"❌ Failed to load SDXL LoRA: {e}")
                self._sdxl_lora = None
        
        logger.info("✅ All image generation models loaded successfully")
    
    def get_llm(self) -> Optional[ChatLlamaCpp]:
        """Get the pre-loaded LLM instance"""
        if self._llm is None:
            logger.warning("⚠️ Pre-loaded LLM not available, loading fresh...")
            self._load_llm()
        return self._llm
    
    def get_sdxl_turbo(self) -> Optional[DiffusionPipeline]:
        """Get the pre-loaded SDXL Turbo instance"""
        if self._sdxl_turbo is None:
            logger.warning("⚠️ Pre-loaded SDXL Turbo not available, loading fresh...")
            self._load_image_models()
        return self._sdxl_turbo
    
    def get_sdxl_lora(self) -> Optional[DiffusionPipeline]:
        """Get the pre-loaded SDXL LoRA instance"""
        if self._sdxl_lora is None:
            logger.warning("⚠️ Pre-loaded SDXL LoRA not available, loading fresh...")
            self._load_image_models()
        return self._sdxl_lora
    
    def get_status(self) -> Dict[str, Any]:
        """Get model status"""
        return {
            'models_loaded': self._models_loaded,
            'llm_ready': self._llm is not None,
            'sdxl_turbo_ready': self._sdxl_turbo is not None,
            'sdxl_lora_ready': self._sdxl_lora is not None,
        }
    
    def reset(self):
        """Reset model manager"""
        logger.info("🔄 Resetting ModelManager...")
        self._models_loaded = False
        self._llm = None
        self._sdxl_turbo = None
        self._sdxl_lora = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("✅ ModelManager reset complete")
    
    def preload_for_pipeline(self):
        """Preload models for pipeline execution.

        The LangGraph pipeline generates images/video through ComfyUI
        (engram_comfy), NOT the in-process diffusers SDXL pipelines — those
        are legacy and only used by test_gui's image_generator path. Preloading
        them here downloads SDXL-base (~7 GB) and loads two diffusers pipelines
        into VRAM on top of llama-cpp's GPU layers and the already-resident
        ComfyUI, which OOM-segfaults the 16 GB 4080. So preload only the
        narrative LLM; diffusers models still lazy-load on demand if a caller
        (test_gui) actually needs them.
        """
        logger.info("🚀 Preloading narrative LLM for pipeline execution...")
        self._load_llm()
        logger.info("✅ LLM ready for pipeline execution (images/video via ComfyUI)")

    def unload_llm(self):
        """Release the narrative LLM's VRAM.

        On a 16 GB GPU the in-process llama-cpp model (~4.4 GB, 35 layers) can't
        coexist with ComfyUI loading Flux (UNET + T5). Once the narrative agents
        have run, the LLM isn't needed for the rest of the dream, so unload it
        before the image/video stage to give ComfyUI the full card. It lazily
        reloads on the next dream via get_llm()/preload_for_pipeline().
        """
        if self._llm is None:
            return
        logger.info("🔻 Unloading narrative LLM to free VRAM for ComfyUI image/video...")
        self._llm = None
        self._models_loaded = False
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("✅ LLM unloaded; VRAM released")
