# Dreams.ai Development Workflow

## Daily Development Process

### Morning Routine (15 minutes)
1. **Pull Latest Changes**
   ```bash
   git pull origin main
   ```

2. **Check System Status**
   ```bash
   cd Backend/Python
   python test_pipeline.py
   ```

3. **Review Agent Pipeline**
   - Check for any failed agent executions
   - Review recent .imn file generations
   - Verify LLM connection status

### Development Session

#### 1. Feature Development
- **Agent Enhancements**: Work on specific agent improvements
- **New Features**: Implement new functionality
- **Bug Fixes**: Address identified issues
- **Documentation**: Update relevant docs

#### 2. Testing Strategy
- **Unit Tests**: Test individual agent functions
- **Integration Tests**: Test full pipeline execution
- **Manual Testing**: Test with sample prompts
- **Regression Testing**: Ensure existing functionality works

#### 3. Code Quality
- **Code Review**: Self-review before committing
- **Documentation**: Update inline comments and docs
- **Error Handling**: Ensure robust error handling
- **Performance**: Monitor execution times

### Evening Routine (10 minutes)
1. **Commit Changes**
   ```bash
   git add .
   git commit -m "descriptive commit message"
   ```

2. **Update Documentation**
   - Update relevant documentation files
   - Note any breaking changes
   - Document new features

3. **Plan Next Session**
   - Review task list
   - Prioritize next items
   - Update project status

## Common Development Tasks

### Adding a New Agent

1. **Create Agent Function**
   ```python
   def NewAgent(state: State):
       """
       New agent description and responsibilities.
       """
       # Agent implementation
       return state
   ```

2. **Add to LangGraph Workflow**
   ```python
   graph_builder.add_node("new_agent", NewAgent)
   graph_builder.add_edge("previous_agent", "new_agent")
   graph_builder.add_edge("new_agent", "next_agent")
   ```

3. **Update State Management**
   - Add new fields to State TypedDict if needed
   - Update state transitions

4. **Test Integration**
   ```bash
   python test_pipeline.py
   ```

### Modifying .imn Schema

1. **Update Schema Documentation**
   - Edit `Backend/Scoping/schema.imn`
   - Document new fields and their purposes

2. **Update Utility Functions**
   ```python
   # In core/imn_utils.py
   def create_imn_structure(...):
       # Add new fields to structure
   ```

3. **Update Agent Functions**
   - Modify agents to handle new fields
   - Add validation for new data

4. **Test Schema Changes**
   ```bash
   python test_pipeline.py
   # Verify .imn files are properly structured
   ```

### Debugging Agent Issues

1. **Check Console Output**
   - Look for error messages
   - Check agent execution logs
   - Verify state transitions

2. **Validate .imn Files**
   ```python
   from core.imn_utils import validate_imn_structure, read_imn
   
   imn_data = read_imn("path/to/file.imn")
   if validate_imn_structure(imn_data):
       print("File structure is valid")
   ```

3. **Test Individual Agents**
   ```python
   # Create test state
   test_state = {
       "messages": [{"role": "user", "content": "test prompt"}],
       "user_id": "test-user"
   }
   
   # Test specific agent
   result = AgentFunction(test_state)
   ```

4. **Check LangGraph State**
   - Verify state transitions
   - Check message flow between agents
   - Validate data persistence

### Performance Optimization

1. **Monitor Execution Times**
   ```python
   import time
   
   start_time = time.time()
   result = agent_function(state)
   execution_time = time.time() - start_time
   print(f"Execution time: {execution_time:.2f} seconds")
   ```

2. **Optimize LLM Calls**
   - Reduce prompt length where possible
   - Cache repeated responses
   - Batch similar requests

3. **File I/O Optimization**
   - Minimize file read/write operations
   - Use efficient JSON serialization
   - Implement caching for frequently accessed files

## Testing Guidelines

### Unit Testing
- Test each agent function independently
- Mock external dependencies (LLM, file system)
- Test error conditions and edge cases

### Integration Testing
- Test complete pipeline execution
- Verify data flow between agents
- Test .imn file generation and validation

### Manual Testing
- Test with various prompt types
- Verify user experience flow
- Check error handling and recovery

### Test Data Management
```python
# Sample test prompts
TEST_PROMPTS = [
    "A corgi taking a nap on a sunny beach",
    "A magical forest adventure",
    "A space exploration mission",
    "A detective solving a mystery"
]
```

## Code Quality Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Keep functions focused and small

### Error Handling
```python
try:
    # Main logic
    result = process_data(data)
except SpecificException as e:
    # Handle specific error
    logger.error(f"Specific error: {e}")
    return fallback_result
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
    return None
```

### Documentation
- Update docstrings for all functions
- Document complex algorithms
- Maintain README and architecture docs
- Comment on non-obvious code sections

## Git Workflow

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical fixes

### Commit Messages
```
type(scope): description

feat(agent): add new Carthir memory persistence
fix(pipeline): resolve JSON parsing error in CarthirReview
docs(readme): update installation instructions
test(pipeline): add comprehensive test suite
```

### Pull Request Process
1. Create feature branch
2. Implement changes
3. Write/update tests
4. Update documentation
5. Create pull request
6. Code review
7. Merge to develop

## Environment Management

### Local Development Setup
```bash
# Backend
cd Backend/Python
pip install -r requirements.txt
python api_server.py

# Frontend
npm install
npm run dev

# Database
# Configure Supabase local development
```

### Environment Variables
```bash
# .env file
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-anon-key
OLLAMA_BASE_URL=http://10.1.95.9:11434
```

### Dependencies Management
```bash
# Update Python dependencies
pip install --upgrade package-name
pip freeze > requirements.txt

# Update Node.js dependencies
npm update package-name
npm audit fix
```

## Monitoring and Logging

### Logging Strategy
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log agent execution
logger.info(f"Agent {agent_name} started")
logger.info(f"Agent {agent_name} completed successfully")
logger.error(f"Agent {agent_name} failed: {error}")
```

### Performance Monitoring
- Track agent execution times
- Monitor LLM response times
- Log file I/O operations
- Track error rates

### Health Checks
```python
def health_check():
    """Check system health and dependencies."""
    checks = {
        "llm_connection": check_llm_connection(),
        "file_system": check_file_permissions(),
        "database": check_database_connection(),
        "agent_pipeline": test_pipeline()
    }
    return all(checks.values())
```

## Troubleshooting Guide

### Common Issues

#### LLM Connection Problems
```bash
# Check Ollama status
curl http://10.1.95.9:11434/api/tags

# Restart Ollama if needed
ollama serve
```

#### File Permission Issues
```bash
# Check directory permissions
ls -la Backend/Python/Dreams/

# Fix permissions if needed
chmod 755 Backend/Python/Dreams/
```

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -r requirements.txt
```

#### Agent Pipeline Failures
1. Check individual agent functions
2. Verify state transitions
3. Validate .imn file structure
4. Review error logs

### Debug Mode
```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"[DEBUG] State: {state}")
print(f"[DEBUG] Agent output: {result}")
```

## Best Practices

### Code Organization
- Keep related functions together
- Use clear, descriptive names
- Separate concerns (agents, utilities, API)
- Maintain consistent file structure

### Error Recovery
- Implement graceful degradation
- Provide meaningful error messages
- Use fallback mechanisms
- Log errors for debugging

### Performance
- Optimize LLM prompts
- Minimize file operations
- Use efficient data structures
- Cache frequently accessed data

### Security
- Validate all inputs
- Sanitize user data
- Use secure authentication
- Implement proper authorization

---

*This workflow guide should be updated as the development process evolves.* 