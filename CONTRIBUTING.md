# Contributing to QuantaEnergi

Thank you for your interest in contributing to QuantaEnergi! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Regional Customizations](#regional-customizations)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose (optional)
- Git

### Setting Up Development Environment

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/QuantaEnergi.git
   cd QuantaEnergi
   ```

2. **Install Dependencies**
   ```bash
   # Install root dependencies
   npm install
   
   # Install backend dependencies
   cd apps/backend
   pip install -r requirements.txt
   
   # Install frontend dependencies
   cd ../frontend
   npm install
   ```

3. **Environment Setup**
   ```bash
   # Copy environment files
   cp backend/config.env.example backend/config.env
   cp frontend/env.example frontend/.env
   
   # Update configuration as needed
   ```

4. **Database Setup**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose up -d postgres redis
   
   # Run migrations
   cd apps/backend
   alembic upgrade head
   ```

5. **Start Development Servers**
   ```bash
   # From project root
   npm run dev
   ```

## Development Workflow

### Branch Strategy

We use Git Flow with the following branches:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `hotfix/*`: Critical bug fixes
- `release/*`: Release preparation branches

### Branch Naming Convention

- `feature/description-of-feature`
- `hotfix/description-of-fix`
- `release/version-number`
- `docs/description-of-docs`

Examples:
- `feature/mobile-app-integration`
- `hotfix/security-vulnerability-fix`
- `release/v2.1.0`
- `docs/api-documentation-update`

## Coding Standards

### Python (Backend)

#### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use type hints for all functions and methods
- Maximum line length: 88 characters

#### Naming Conventions
```python
# Variables and functions: snake_case
user_id = "123"
def calculate_var():
    pass

# Classes: PascalCase
class RiskCalculator:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
```

#### Documentation
```python
def calculate_value_at_risk(
    portfolio: Portfolio,
    confidence_level: float,
    time_horizon: int
) -> float:
    """
    Calculate Value at Risk (VaR) for a given portfolio.
    
    Args:
        portfolio: Portfolio object containing positions and market data
        confidence_level: Confidence level for VaR calculation (e.g., 0.95 for 95%)
        time_horizon: Time horizon in days
        
    Returns:
        VaR value as a float
        
    Raises:
        ValidationError: If portfolio is invalid
        CalculationError: If VaR calculation fails
        
    Example:
        >>> portfolio = Portfolio(positions=[...])
        >>> var = calculate_value_at_risk(portfolio, 0.95, 1)
        >>> print(f"VaR: ${var:.2f}")
    """
    pass
```

### TypeScript/React (Frontend)

#### Code Style
- Use ESLint and Prettier configurations
- Prefer functional components with hooks
- Use TypeScript strict mode
- Maximum line length: 80 characters

#### Naming Conventions
```typescript
// Variables and functions: camelCase
const userId = "123";
const calculateVar = () => {};

// Components: PascalCase
const RiskCalculator: React.FC = () => {};

// Types and interfaces: PascalCase
interface RiskMetrics {
  var95: number;
  var99: number;
}

// Constants: UPPER_SNAKE_CASE
const MAX_RETRY_ATTEMPTS = 3;
```

#### Component Documentation
```typescript
/**
 * RiskCalculator component for calculating portfolio risk metrics
 * 
 * @param portfolio - Portfolio data for risk calculation
 * @param onCalculate - Callback function when calculation is complete
 * @param isLoading - Loading state indicator
 * @returns JSX element with risk calculation interface
 */
interface RiskCalculatorProps {
  portfolio: Portfolio;
  onCalculate: (metrics: RiskMetrics) => void;
  isLoading: boolean;
}

const RiskCalculator: React.FC<RiskCalculatorProps> = ({
  portfolio,
  onCalculate,
  isLoading
}) => {
  // Component implementation
};
```

## Testing Guidelines

### Backend Testing

#### Unit Tests
- Test coverage must be at least 80%
- Use pytest for testing framework
- Mock external dependencies
- Test both success and failure scenarios

```python
import pytest
from unittest.mock import Mock, patch
from app.services.risk_calculator import RiskCalculator

class TestRiskCalculator:
    def test_calculate_var_success(self):
        """Test successful VaR calculation"""
        calculator = RiskCalculator()
        portfolio = Mock()
        portfolio.positions = [{"commodity": "crude_oil", "quantity": 100}]
        
        result = calculator.calculate_var(portfolio, 0.95, 1)
        
        assert result > 0
        assert isinstance(result, float)
    
    def test_calculate_var_invalid_portfolio(self):
        """Test VaR calculation with invalid portfolio"""
        calculator = RiskCalculator()
        
        with pytest.raises(ValidationError):
            calculator.calculate_var(None, 0.95, 1)
```

#### Integration Tests
- Test API endpoints
- Test database operations
- Test external service integrations

```python
def test_trade_creation_api(client, auth_headers):
    """Test trade creation via API"""
    trade_data = {
        "trade_type": "spot",
        "commodity_type": "crude_oil",
        "quantity": 100,
        "price": 75.50,
        "currency": "USD"
    }
    
    response = client.post(
        "/api/v1/trades",
        json=trade_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json()["trade_id"] is not None
```

### Frontend Testing

#### Component Tests
- Use React Testing Library
- Test user interactions
- Test component rendering

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { RiskCalculator } from './RiskCalculator';

describe('RiskCalculator', () => {
  it('renders calculator interface', () => {
    render(<RiskCalculator portfolio={mockPortfolio} onCalculate={jest.fn()} />);
    
    expect(screen.getByText('Calculate Risk')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /calculate/i })).toBeInTheDocument();
  });

  it('calls onCalculate when calculate button is clicked', () => {
    const mockOnCalculate = jest.fn();
    render(<RiskCalculator portfolio={mockPortfolio} onCalculate={mockOnCalculate} />);
    
    fireEvent.click(screen.getByRole('button', { name: /calculate/i }));
    
    expect(mockOnCalculate).toHaveBeenCalled();
  });
});
```

## Documentation Standards

### API Documentation
- Use OpenAPI/Swagger specifications
- Include examples for all endpoints
- Document error responses
- Keep documentation up to date

### Code Documentation
- Use docstrings for all functions and classes
- Include type hints
- Provide examples where helpful
- Update documentation with code changes

### README Files
- Include setup instructions
- Provide usage examples
- List dependencies
- Include contribution guidelines

## Pull Request Process

### Before Submitting

1. **Run Tests**
   ```bash
   # Backend tests
   cd apps/backend
   pytest tests/ -v --cov=app
   
   # Frontend tests
   cd apps/frontend
   npm test
   ```

2. **Run Linting**
   ```bash
   # Backend linting
   cd apps/backend
   black . && flake8 . && mypy .
   
   # Frontend linting
   cd apps/frontend
   npm run lint
   ```

3. **Update Documentation**
   - Update CHANGELOG.md if applicable
   - Update API documentation if endpoints changed
   - Update README if setup instructions changed

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] CHANGELOG.md updated (if applicable)

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Additional Notes
Any additional information or context about the changes.
```

### Review Process

1. **Automated Checks**
   - All tests must pass
   - Code must pass linting
   - Coverage must not decrease

2. **Manual Review**
   - Code quality and style
   - Security implications
   - Performance impact
   - Documentation completeness

3. **Approval Requirements**
   - At least one approval from maintainers
   - All discussions resolved
   - All checks passing

## Issue Guidelines

### Bug Reports

Use the bug report template and include:

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment (please complete the following information):**
- OS: [e.g. Windows, macOS, Linux]
- Browser: [e.g. Chrome, Safari, Firefox]
- Version: [e.g. 22]
- Python version: [e.g. 3.12]
- Node version: [e.g. 18.17]

**Additional context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template and include:

```markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## Regional Customizations

We welcome contributions for regional customizations, especially for:

### Middle East & Islamic Finance
- Arabic language support
- RTL (Right-to-Left) UI layouts
- Islamic calendar integration
- Sharia compliance enhancements

### United States
- CFTC reporting improvements
- FERC compliance features
- NERC standards integration

### European Union & UK
- EMIR reporting enhancements
- GDPR compliance features
- ACER requirements

### Guyana
- Local currency support (GYD)
- Regional regulatory compliance
- Local market data integration

### Guidelines for Regional Contributions

1. **Research Requirements**
   - Understand local regulations
   - Study existing implementations
   - Consult with local experts

2. **Implementation Approach**
   - Create feature flags for regional features
   - Maintain backward compatibility
   - Add comprehensive tests

3. **Documentation**
   - Document regional requirements
   - Provide usage examples
   - Include regulatory references

## Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord**: For real-time chat (invite link in README)

### Resources

- [API Documentation](docs/api.md)
- [Architecture Guide](docs/architecture/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [User Guide](docs/user_guide.md)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to QuantaEnergi! 🚀
