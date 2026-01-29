# Contributing to Supply Chain Finance Platform

Thank you for your interest in contributing to our platform! This document outlines the process and guidelines for contributing.

## Development Setup

1. **Environment Setup**
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd supplychain-finance-platform
   
   # Install dependencies
   make setup
   make install
   ```

2. **Running Tests**
   ```bash
   # Run all tests
   make test
   
   # Run specific test suites
   make test-backend
   make test-frontend
   make test-blockchain
   ```

## Development Guidelines

### Code Style
- Frontend: Follow React/TypeScript best practices
- Backend: Follow Java Spring Boot conventions
- Blockchain: Follow Solidity style guide
- Use ESLint and Prettier for code formatting

### Git Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Description of changes"`
4. Push to your fork: `git push origin feature/your-feature`
5. Submit a Pull Request

### Pull Request Process
1. Ensure all tests pass
2. Update documentation if needed
3. Add test cases for new features
4. Get approval from two maintainers
5. Squash commits before merging

### Documentation
- Update API documentation for endpoint changes
- Document new features in the relevant guides
- Update architecture diagrams if needed

## Best Practices

### Microservices
- Keep services small and focused
- Follow API-first design
- Implement proper error handling
- Add monitoring and logging

### Security
- Follow security best practices
- Never commit secrets
- Implement proper authentication
- Add security tests

## Getting Help
- Join our Slack channel
- Check existing issues
- Ask in our discussion forum

## License Notice
By contributing to this project, you agree that your contributions will be licensed under our proprietary license. All rights reserved.
