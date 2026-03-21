"""Cost Calculator Service for estimating and calculating development costs."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Platform(str, Enum):
    """Supported mobile platforms."""

    IOS = "ios"
    ANDROID = "android"
    FLUTTER = "flutter"
    REACT_NATIVE = "react_native"
    UNKNOWN = "unknown"


class TaskComplexity(str, Enum):
    """Task complexity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ArchitectureType(str, Enum):
    """Architecture patterns."""

    MVC = "mvc"
    MVVM = "mvvm"
    CLEAN = "clean"
    VIPER = "viper"


# Pricing constants (USD)
TOKEN_PRICE_INPUT = 0.000003  # $3 per 1M tokens
TOKEN_PRICE_OUTPUT = 0.000015  # $15 per 1M tokens
HOURLY_COST_DEVELOPER = 50  # Average developer hourly rate

# Complexity multipliers for time estimation
COMPLEXITY_MULTIPLIERS = {
    TaskComplexity.LOW: 1.0,
    TaskComplexity.MEDIUM: 2.0,
    TaskComplexity.HIGH: 4.0,
    TaskComplexity.VERY_HIGH: 8.0,
}

# Platform complexity factors
PLATFORM_COMPLEXITY = {
    Platform.IOS: 1.2,
    Platform.ANDROID: 1.2,
    Platform.FLUTTER: 0.8,
    Platform.REACT_NATIVE: 0.9,
    Platform.UNKNOWN: 1.0,
}

# Token estimation per task complexity (input + output tokens)
TOKEN_ESTIMATES = {
    TaskComplexity.LOW: {"input": 2000, "output": 4000},
    TaskComplexity.MEDIUM: {"input": 8000, "output": 15000},
    TaskComplexity.HIGH: {"input": 20000, "output": 40000},
    TaskComplexity.VERY_HIGH: {"input": 50000, "output": 100000},
}

# Base hours per task type
BASE_HOURS = {
    "ui_screen": 4,
    "api_integration": 8,
    "database_model": 6,
    "business_logic": 10,
    "testing": 6,
    "refactoring": 8,
    "bug_fix": 2,
    "feature": 12,
    "architecture": 16,
}


@dataclass
class CostEstimate:
    """Container for cost estimation results."""

    estimated_tokens_input: int
    estimated_tokens_output: int
    estimated_hours: float
    estimated_cost: float
    breakdown: dict[str, Any]


class CostCalculator:
    """Service for estimating and calculating development costs."""

    def estimate_time(
        self,
        task_type: str,
        complexity: TaskComplexity,
        platform: Platform = Platform.UNKNOWN,
        lines_of_code: int = 0,
    ) -> float:
        """
        Estimate time required for a task.

        Args:
            task_type: Type of task (ui_screen, api_integration, etc.)
            complexity: Task complexity level
            platform: Target mobile platform
            lines_of_code: Expected lines of code to be written

        Returns:
            Estimated hours as float
        """
        # Get base hours for task type
        base = BASE_HOURS.get(task_type, 10)

        # Apply complexity multiplier
        complexity_mult = COMPLEXITY_MULTIPLIERS.get(complexity, 1.0)

        # Apply platform factor
        platform_mult = PLATFORM_COMPLEXITY.get(platform, 1.0)

        # Calculate base estimate
        hours = base * complexity_mult * platform_mult

        # Adjust for lines of code (rough estimate: 10 lines/hour)
        if lines_of_code > 0:
            hours += lines_of_code / 10

        return round(hours, 2)

    def estimate_tokens(
        self,
        task_type: str,
        complexity: TaskComplexity,
    ) -> tuple[int, int]:
        """
        Estimate token consumption for a task.

        Args:
            task_type: Type of task
            complexity: Task complexity level

        Returns:
            Tuple of (input_tokens, output_tokens)
        """
        estimates = TOKEN_ESTIMATES.get(complexity, TOKEN_ESTIMATES[TaskComplexity.MEDIUM])
        return estimates["input"], estimates["output"]

    def calculate_cost(
        self,
        task_type: str,
        complexity: TaskComplexity,
        platform: Platform = Platform.UNKNOWN,
        lines_of_code: int = 0,
    ) -> CostEstimate:
        """
        Calculate complete cost estimate for a task.

        Args:
            task_type: Type of task
            complexity: Task complexity level
            platform: Target mobile platform
            lines_of_code: Expected lines of code

        Returns:
            CostEstimate with detailed breakdown
        """
        # Get estimates
        input_tokens, output_tokens = self.estimate_tokens(task_type, complexity)
        hours = self.estimate_time(task_type, complexity, platform, lines_of_code)

        # Calculate costs
        input_cost = input_tokens * TOKEN_PRICE_INPUT
        output_cost = output_tokens * TOKEN_PRICE_OUTPUT
        labor_cost = hours * HOURLY_COST_DEVELOPER
        total_cost = input_cost + output_cost + labor_cost

        breakdown = {
            "input_token_cost": round(input_cost, 4),
            "output_token_cost": round(output_cost, 4),
            "labor_cost": round(labor_cost, 2),
            "token_cost": round(input_cost + output_cost, 4),
            "total_cost": round(total_cost, 2),
            "currency": "USD",
            "platform": platform.value,
            "complexity": complexity.value,
            "task_type": task_type,
        }

        return CostEstimate(
            estimated_tokens_input=input_tokens,
            estimated_tokens_output=output_tokens,
            estimated_hours=hours,
            estimated_cost=round(total_cost, 2),
            breakdown=breakdown,
        )

    def calculate_batch_costs(
        self,
        tasks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Calculate costs for multiple tasks.

        Args:
            tasks: List of task dictionaries with type, complexity, platform, loc

        Returns:
            Summary with per-task and total costs
        """
        results = []
        total_cost = 0.0
        total_tokens_input = 0
        total_tokens_output = 0
        total_hours = 0.0

        for task in tasks:
            estimate = self.calculate_cost(
                task_type=task.get("type", "feature"),
                complexity=TaskComplexity(task.get("complexity", "medium")),
                platform=Platform(task.get("platform", "unknown")),
                lines_of_code=task.get("lines_of_code", 0),
            )

            results.append({
                "task_id": task.get("id"),
                "task_title": task.get("title", "Unknown"),
                **estimate.breakdown,
            })

            total_cost += estimate.estimated_cost
            total_tokens_input += estimate.estimated_tokens_input
            total_tokens_output += estimate.estimated_tokens_output
            total_hours += estimate.estimated_hours

        return {
            "tasks": results,
            "summary": {
                "total_cost": round(total_cost, 2),
                "total_tokens_input": total_tokens_input,
                "total_tokens_output": total_tokens_output,
                "total_hours": round(total_hours, 2),
                "task_count": len(tasks),
                "currency": "USD",
            },
        }

    def calculate_actual_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        duration_seconds: int,
    ) -> dict[str, Any]:
        """
        Calculate actual cost from usage metrics.

        Args:
            input_tokens: Actual input tokens consumed
            output_tokens: Actual output tokens consumed
            duration_seconds: Task duration in seconds

        Returns:
            Dictionary with actual cost breakdown
        """
        input_cost = input_tokens * TOKEN_PRICE_INPUT
        output_cost = output_tokens * TOKEN_PRICE_OUTPUT
        hours = duration_seconds / 3600
        labor_cost = hours * HOURLY_COST_DEVELOPER

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "duration_seconds": duration_seconds,
            "duration_hours": round(hours, 2),
            "input_cost": round(input_cost, 4),
            "output_cost": round(output_cost, 4),
            "labor_cost": round(labor_cost, 2),
            "total_token_cost": round(input_cost + output_cost, 4),
            "total_cost": round(input_cost + output_cost + labor_cost, 2),
            "currency": "USD",
        }


# Global instance
cost_calculator = CostCalculator()
