# Skills Configuration

## Available Skills

List and configure skills that the agent should use for this project.

### Skill Format

```markdown
- **Skill Name**: Brief description
  - Path: `/path/to/skill/folder`
  - When to use: Specific scenarios where this skill applies
```

### Example Skills

- **Python Testing**: Use pytest for all Python testing tasks
  - When to use: When writing or running Python tests
  
- **Code Review**: Perform comprehensive code reviews
  - When to use: Before merging changes
  
- **Documentation**: Generate and maintain project documentation
  - When to use: When creating new features or updating existing ones

## Notes

- Skills are specialized instruction sets stored in folders
- Each skill folder should contain a SKILL.md file with detailed instructions
- The agent will read SKILL.md when the skill is relevant to the task
