# Performance Optimization Plan: 10-Second Dream Generation

**Date:** July 20, 2025  
**Target:** Reduce dream generation time from 49s to 10s (80% improvement)  
**Status:** Updated for Parallel, Primed Agents & Seamless UX

## Executive Summary

The Dreams.ai pipeline aims to deliver a complete dream—including the first image prompt—within 10 seconds. This is achieved by priming agents in a warm pool, executing all agents in parallel using a shared IMN file, streaming progressive updates to the frontend, and caching all outputs (including partial and fallback results). The user experience is designed to be seamless, with real-time feedback and instant placeholder responses.

## Current Performance Analysis

### Pipeline Breakdown
```
Carthir (49s) → convert_prompt → Narnion → CarthirReview → Cenedril → END
```

**Detailed Timing:**
- **Carthir**: 49.34s (99.96% of total time) - LLM call for dream pitch
- **Narnion**: ~2-3s - LLM call for scene generation  
- **CarthirReview**: ~2-3s - LLM call for director vision
- **Cenedril**: ~1s - LLM call for image prompt
- **File Operations**: <0.01s - IMN file read/write

### Bottlenecks Identified (Previous Architecture)
1. **Sequential Processing**: Agents run one after another
2. **LLM API Latency**: Each agent waits for Ollama response
3. **No Caching**: Similar prompts processed repeatedly
4. **Blocking Operations**: User waits for complete pipeline
5. **No Streaming**: No real-time feedback to user

## New Architecture: Primed Parallel Agents & Seamless UX

### Key Principles
- **Agents Primed and Ready**: Agents are loaded and kept warm in a pool, reducing cold start latency.
- **Parallel Agent Execution**: All agents (Carthir, Narnion, Cenedril, etc.) start simultaneously, using a shared IMN file for state.
- **Progressive Streaming**: As each agent completes, updates are streamed to the frontend in real time (WebSockets/SSE).
- **Cache All Outputs**: All agent outputs—including partial and fallback results—are cached for future similar prompts.
- **Seamless UX**: Users receive instant placeholder feedback, progressive updates, and the first image prompt within 10 seconds.

### Logical Flow (User Journey)
1. **User submits prompt**.
2. **Immediate Response**: 
   - Check cache for similar prompt. If found, return cached result instantly.
   - If not, create placeholder dream card and IMN file.
3. **Parallel Agent Start**:
   - All agents start in parallel, reading from and writing to the IMN file (with file locking/atomic ops).
   - Each agent updates its section of the IMN as soon as it completes.
4. **Progressive Streaming**:
   - As soon as the image prompt (Cenedril) is ready, push it to the frontend (even if other agents are still running).
   - Continue updating the frontend as more data becomes available.
5. **Cache Results**:
   - Cache all agent outputs (including partial/fallbacks) for future similar prompts.

### Example: Parallel Agent Orchestration (Pseudocode)
```python
from concurrent.futures import ThreadPoolExecutor
import threading

def run_agents_in_parallel(prompt, user_id, imn_path):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            'carthir': executor.submit(run_carthir, prompt, imn_path),
            'narnion': executor.submit(run_narnion, prompt, imn_path),
            'cenedril': executor.submit(run_cenedril, prompt, imn_path)
        }
        # Stream updates as each completes
        for name, future in futures.items():
            result = future.result(timeout=8)
            # Update IMN file and notify frontend
```

### UX Example: Progressive Dream Card
- **0s**: “Generating your dream…” (placeholder)
- **2–4s**: “Story ready!” (Carthir/Narnion done)
- **6–8s**: “Image prompt ready!” (Cenedril done, show image)
- **10s**: “Dream complete!” (all agents done)

## Implementation Plan

### Phase 1: Agent Pooling & Priming
- [ ] Implement a pool of pre-loaded agent processes/models (warm pool)
- [ ] Add health checks and idle timeouts for unloading

### Phase 2: Parallel Execution Framework
- [ ] Refactor agent orchestration to use a thread/process pool
- [ ] Implement file locking for safe IMN file updates
- [ ] Ensure agents can operate independently and in parallel

### Phase 3: Progressive Streaming
- [ ] Add backend support for streaming updates (WebSockets/SSE)
- [ ] Update frontend to handle and display progressive updates

### Phase 4: Caching & Optimization
- [ ] Cache all agent outputs, including partial/fallbacks
- [ ] Use semantic similarity for cache lookups
- [ ] Monitor and tune for performance

## Success Metrics
- **First Image Prompt**: ≤10 seconds from user submission
- **Initial Response**: <1 second for placeholder card
- **Cache Hit Rate**: >30% for similar prompts
- **User Satisfaction**: Seamless, real-time feedback
- **Resource Usage**: Efficient agent pooling and memory management
- **Error Rate**: <5% timeout or failure rate
- **Scalability**: Support 10+ concurrent users

## Technical Considerations
- **File Locking**: Use platform-appropriate file locking for IMN file access, or consider a lightweight DB (e.g., SQLite) for concurrent writes.
- **Agent Communication**: Use message queues for coordination if scaling out.
- **Frontend**: Use React state to show progressive updates and loading indicators.

## Risk Assessment
- **Thread Safety**: Mitigated by file locking/atomic ops
- **Memory Usage**: Managed by warm pool size and idle timeouts
- **API Rate Limits**: Mitigated by request throttling and caching
- **Response Quality**: Progressive enhancement and fallback caching
- **Cache Staleness**: Invalidation and versioning
- **Error Propagation**: Graceful degradation and retry logic

## Future Enhancements
- **Model Optimization**: Use quantized/distilled models for faster inference
- **Edge Caching**: Distribute cache across nodes
- **Predictive Loading**: Pre-generate common responses
- **Adaptive Timeouts**: Dynamic timeout based on load
- **Real-time Collaboration**: Multiple users on same dream
- **Dream Templates**: Pre-built dream structures
- **Batch Processing**: Multiple dreams at once
- **Offline Mode**: Cached responses when API unavailable

## Conclusion

This updated plan provides a clear, actionable roadmap to achieve the 10-second target for dream generation. By priming agents, running them in parallel, streaming progressive updates, and caching all outputs, we ensure a seamless, high-performance user experience.

**Key Success Factors:**
1. **Primed Agents**: No cold start delays
2. **Parallel Processing**: All agents run simultaneously
3. **Progressive Streaming**: Real-time feedback to user
4. **Comprehensive Caching**: All outputs cached for future use
5. **Seamless UX**: Immediate and progressive updates

**Expected Outcome**: 80%+ reduction in response time (49s → 10s) with a world-class, responsive user experience.

---

**Next Steps**: Begin implementation with agent pooling, parallel execution, and progressive streaming framework. 