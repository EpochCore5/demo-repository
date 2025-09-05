# Contributing Guidelines

Thank you for your interest in contributing to the EpochCore5 Demo Repository! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or suggest features
- Check if the issue already exists before creating a new one
- Provide detailed steps to reproduce the issue
- Include environment details (OS, Python version, etc.)
- For security vulnerabilities, please follow our [Security Policy](SECURITY.md)

### Pull Requests

1. Fork the repository
2. Create a new branch from `main` (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run the security scanner (`./scan_security.sh`)
5. Commit your changes with signed commits (`git commit -S -m "Your message"`)
6. Push to your branch (`git push origin feature/your-feature-name`)
7. Create a Pull Request targeting the `main` branch

### Pull Request Requirements

All pull requests must:

- Follow the PR template
- Include tests for new functionality
- Pass all CI checks including security scanning
- Be reviewed by at least one maintainer
- Maintain or improve code coverage
- Update documentation as needed
- Be signed with a GPG key

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Keep functions small and focused
- Document complex logic with inline comments
- Use meaningful variable and function names

### Documentation

- Update documentation for any changed functionality
- Document public APIs with docstrings
- Keep README and other guides up to date
- Include examples for new features

### Testing

- Write unit tests for all new features
- Maintain or improve code coverage
- Include integration tests when appropriate
- Test edge cases and error conditions

### Agent Development

When developing or modifying agents:

1. Follow the agent development guidelines in `docs/agent_management.md`
2. Ensure proper audit trails are maintained
3. Update agent manifests with proper versioning
4. Test agent interactions with the recursive system
5. Document agent capabilities and limitations

### Security Considerations

- Never commit credentials or secrets
- Follow secure coding practices
- Use the principle of least privilege
- Run security scans before submitting PRs
- Report security vulnerabilities according to our [Security Policy](SECURITY.md)

## Governance

This project follows a governance model defined by:

- **Administrators**: Responsible for overall project direction and security
- **Core Developers**: Responsible for codebase development and maintenance
- **Agent Operators**: Responsible for agent configuration and management
- **Auditors**: Responsible for compliance and audit review
- **Security Team**: Responsible for security configurations and reviews

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

## Getting Help

If you need help with contributing:

- Review the documentation in the `docs/` directory
- Join our [community discussion forum](https://community.epochcore5.com)
- Contact the maintainers for specific questions

Thank you for contributing to EpochCore5!
