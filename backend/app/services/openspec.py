"""OpenSpec service for generating requirement proposals, designs, specs, and tasks."""

import uuid
from datetime import datetime
from typing import Any


class OpenSpecService:
    """Service class for OpenSpec document generation.

    This service generates standardized requirement documentation including:
    - Proposal: Initial requirement analysis and overview
    - Design: Technical architecture design
    - Specs: Functional specification breakdown
    - Tasks: Implementation task list
    """

    def __init__(self):
        """Initialize OpenSpec service with in-memory storage."""
        self._store: dict[str, dict] = {}

    async def generate_proposal(
        self,
        project_id: str,
        title: str,
        description: str,
        platform: str = "android",
        requirements: list[str] | None = None,
    ) -> dict:
        """Generate a requirement proposal document.

        Args:
            project_id: Project identifier
            title: Project or feature title
            description: Detailed requirement description
            platform: Target platform (android/ios/harmony)
            requirements: List of specific requirements

        Returns:
            dict containing the generated proposal
        """
        proposal_id = str(uuid.uuid4())
        now = datetime.now()

        # Analyze requirements complexity
        complexity = self._calculate_complexity(description, requirements or [])

        proposal = {
            "id": proposal_id,
            "project_id": project_id,
            "title": title,
            "description": description,
            "platform": platform,
            "requirements": requirements or [],
            "complexity": complexity,
            "estimated_hours": self._estimate_hours(complexity),
            "status": "proposal",
            "created_at": now,
            "updated_at": now,
            "content": self._generate_proposal_content(
                title, description, platform, requirements or [], complexity
            ),
        }

        self._store[proposal_id] = proposal
        return proposal

    async def generate_design(
        self,
        project_id: str,
        proposal: dict,
        tech_stack: list[str] | None = None,
    ) -> dict:
        """Generate technical architecture design document.

        Args:
            project_id: Project identifier
            proposal: The proposal document from generate_proposal
            tech_stack: Technology stack to use

        Returns:
            dict containing the generated design
        """
        design_id = str(uuid.uuid4())
        now = datetime.now()

        tech_stack = tech_stack or self._infer_tech_stack(proposal.get("platform", "android"))

        design = {
            "id": design_id,
            "project_id": project_id,
            "proposal_id": proposal.get("id"),
            "title": f"Design: {proposal.get('title', 'Untitled')}",
            "platform": proposal.get("platform", "android"),
            "tech_stack": tech_stack,
            "architecture": self._generate_architecture(tech_stack),
            "components": self._generate_components(tech_stack),
            "data_models": self._generate_data_models(proposal),
            "created_at": now,
            "updated_at": now,
            "content": self._generate_design_content(proposal, tech_stack),
        }

        self._store[design_id] = design
        return design

    async def generate_specs(
        self,
        project_id: str,
        design: dict,
    ) -> list[dict]:
        """Generate functional specification breakdown.

        Args:
            project_id: Project identifier
            design: The design document from generate_design

        Returns:
            list of specification items
        """
        specs = []
        now = datetime.now()

        # Generate specs based on components
        components = design.get("components", [])
        for i, component in enumerate(components):
            spec_id = str(uuid.uuid4())
            spec = {
                "id": spec_id,
                "project_id": project_id,
                "design_id": design.get("id"),
                "component": component.get("name"),
                "type": component.get("type", "feature"),
                "title": f"Spec: {component.get('name', f'Component {i+1}')}",
                "description": component.get("description", ""),
                "functional_requirements": self._generate_functional_requirements(component),
                "non_functional_requirements": self._generate_nfr(component),
                "acceptance_criteria": self._generate_acceptance_criteria(component),
                "priority": component.get("priority", "medium"),
                "estimated_hours": component.get("estimated_hours", 4),
                "created_at": now,
                "updated_at": now,
            }
            specs.append(spec)
            self._store[spec_id] = spec

        return specs

    async def generate_tasks(
        self,
        project_id: str,
        specs: list[dict],
    ) -> list[dict]:
        """Generate implementation task list from specs.

        Args:
            project_id: Project identifier
            specs: List of specification items

        Returns:
            list of implementation tasks
        """
        tasks = []
        now = datetime.now()
        task_order = 0

        for spec in specs:
            spec_tasks = self._generate_tasks_from_spec(spec, task_order)
            task_order += len(spec_tasks)

            for task in spec_tasks:
                task_id = str(uuid.uuid4())
                full_task = {
                    "id": task_id,
                    "project_id": project_id,
                    "spec_id": spec.get("id"),
                    "title": task.get("title"),
                    "description": task.get("description"),
                    "type": task.get("type", "feature"),
                    "priority": task.get("priority", "medium"),
                    "estimated_hours": task.get("estimated_hours", 1),
                    "dependencies": task.get("dependencies", []),
                    "status": "pending",
                    "created_at": now,
                    "updated_at": now,
                }
                tasks.append(full_task)
                self._store[task_id] = full_task

        return tasks

    async def generate_full(
        self,
        project_id: str,
        title: str,
        description: str,
        platform: str = "android",
        requirements: list[str] | None = None,
        tech_stack: list[str] | None = None,
    ) -> dict:
        """Generate complete OpenSpec documentation in one flow.

        Args:
            project_id: Project identifier
            title: Project or feature title
            description: Detailed requirement description
            platform: Target platform
            requirements: List of specific requirements
            tech_stack: Technology stack

        Returns:
            dict containing proposal, design, specs, and tasks
        """
        # Step 1: Generate proposal
        proposal = await self.generate_proposal(
            project_id=project_id,
            title=title,
            description=description,
            platform=platform,
            requirements=requirements,
        )

        # Step 2: Generate design
        design = await self.generate_design(
            project_id=project_id,
            proposal=proposal,
            tech_stack=tech_stack,
        )

        # Step 3: Generate specs
        specs = await self.generate_specs(
            project_id=project_id,
            design=design,
        )

        # Step 4: Generate tasks
        tasks = await self.generate_tasks(
            project_id=project_id,
            specs=specs,
        )

        return {
            "project_id": project_id,
            "proposal": proposal,
            "design": design,
            "specs": specs,
            "tasks": tasks,
            "generated_at": datetime.now(),
        }

    def get_document(self, doc_id: str) -> dict | None:
        """Get a document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document dict or None if not found
        """
        return self._store.get(doc_id)

    def get_proposal(self, project_id: str) -> dict | None:
        """Get the latest proposal for a project.

        Args:
            project_id: Project identifier

        Returns:
            Proposal dict or None if not found
        """
        proposals = [
            doc for doc in self._store.values()
            if doc.get("project_id") == project_id and doc.get("status") == "proposal"
        ]
        return proposals[-1] if proposals else None

    def get_design(self, project_id: str) -> dict | None:
        """Get the latest design for a project.

        Args:
            project_id: Project identifier

        Returns:
            Design dict or None if not found
        """
        designs = [
            doc for doc in self._store.values()
            if doc.get("project_id") == project_id and "architecture" in doc
        ]
        return designs[-1] if designs else None

    def get_specs(self, project_id: str) -> list[dict]:
        """Get all specs for a project.

        Args:
            project_id: Project identifier

        Returns:
            List of spec dicts
        """
        return [
            doc for doc in self._store.values()
            if doc.get("project_id") == project_id and "functional_requirements" in doc
        ]

    def get_tasks(self, project_id: str) -> list[dict]:
        """Get all tasks for a project.

        Args:
            project_id: Project identifier

        Returns:
            List of task dicts
        """
        return [
            doc for doc in self._store.values()
            if doc.get("project_id") == project_id and doc.get("status") == "pending"
        ]

    # Private helper methods

    def _calculate_complexity(
        self,
        description: str,
        requirements: list[str],
    ) -> str:
        """Calculate complexity level based on description and requirements."""
        score = 0

        # Base score from description length
        score += len(description) // 200

        # Add score for each requirement
        score += len(requirements)

        # Check for complexity indicators
        complexity_keywords = [
            "authentication", "database", "api", "integration",
            "payment", "notification", "offline", "sync",
            "real-time", "streaming", "ml", "ai",
        ]
        description_lower = description.lower()
        for keyword in complexity_keywords:
            if keyword in description_lower:
                score += 2

        if score <= 3:
            return "low"
        elif score <= 7:
            return "medium"
        else:
            return "high"

    def _estimate_hours(self, complexity: str) -> float:
        """Estimate hours based on complexity."""
        base_hours = {
            "low": 8,
            "medium": 24,
            "high": 48,
        }
        return base_hours.get(complexity, 24)

    def _infer_tech_stack(self, platform: str) -> list[str]:
        """Infer technology stack from platform."""
        stacks = {
            "android": ["Kotlin", "Jetpack Compose", "MVVM", "Hilt", "Room"],
            "ios": ["Swift", "SwiftUI", "MVVM", "Combine", "CoreData"],
            "harmony": ["ArkTS", "ArkUI", "Stage", "HDF"],
        }
        return stacks.get(platform.lower(), stacks["android"])

    def _generate_architecture(self, tech_stack: list[str]) -> dict:
        """Generate architecture diagram structure."""
        return {
            "type": "layered",
            "layers": [
                {"name": "Presentation", "components": ["UI", "ViewModel"]},
                {"name": "Domain", "components": ["Use Cases", "Entities"]},
                {"name": "Data", "components": ["Repositories", "Data Sources"]},
            ],
            "pattern": "MVVM",
        }

    def _generate_components(self, tech_stack: list[str]) -> list[dict]:
        """Generate application components based on tech stack."""
        return [
            {
                "name": "UI Layer",
                "type": "presentation",
                "description": "User interface components and screens",
                "priority": "high",
                "estimated_hours": 8,
            },
            {
                "name": "ViewModel",
                "type": "presentation",
                "description": "UI state management and business logic binding",
                "priority": "high",
                "estimated_hours": 4,
            },
            {
                "name": "Repository",
                "type": "data",
                "description": "Data access abstraction layer",
                "priority": "high",
                "estimated_hours": 4,
            },
            {
                "name": "Data Sources",
                "type": "data",
                "description": "Local and remote data sources",
                "priority": "medium",
                "estimated_hours": 6,
            },
            {
                "name": "Domain Models",
                "type": "domain",
                "description": "Core business entities",
                "priority": "high",
                "estimated_hours": 2,
            },
        ]

    def _generate_data_models(self, proposal: dict) -> list[dict]:
        """Generate data models based on proposal."""
        return [
            {
                "name": "User",
                "fields": [
                    {"name": "id", "type": "UUID"},
                    {"name": "username", "type": "String"},
                    {"name": "email", "type": "String"},
                    {"name": "created_at", "type": "DateTime"},
                ],
            },
            {
                "name": "Project",
                "fields": [
                    {"name": "id", "type": "UUID"},
                    {"name": "name", "type": "String"},
                    {"name": "description", "type": "String"},
                    {"name": "platform", "type": "String"},
                    {"name": "status", "type": "String"},
                ],
            },
        ]

    def _generate_proposal_content(
        self,
        title: str,
        description: str,
        platform: str,
        requirements: list[str],
        complexity: str,
    ) -> dict:
        """Generate proposal content structure."""
        return {
            "summary": f"Development of {title} for {platform} platform",
            "background": description,
            "goals": [
                f"Implement {title} feature",
                f"Ensure {platform} platform compatibility",
                "Follow mobile development best practices",
            ],
            "requirements": [
                {"id": f"REQ-{i+1}", "text": req, "priority": "must"}
                for i, req in enumerate(requirements)
            ],
            "constraints": [
                f"Target platform: {platform}",
                f"Complexity: {complexity}",
            ],
            "success_metrics": [
                "All acceptance criteria met",
                "Code coverage > 70%",
                "No critical bugs",
            ],
        }

    def _generate_design_content(
        self,
        proposal: dict,
        tech_stack: list[str],
    ) -> dict:
        """Generate design content structure."""
        return {
            "architecture": self._generate_architecture(tech_stack),
            "tech_stack": tech_stack,
            "components": self._generate_components(tech_stack),
            "data_models": self._generate_data_models(proposal),
            "sequence_diagrams": [],
            "api_design": {
                "rest_endpoints": [],
                "websocket_events": [],
            },
        }

    def _generate_functional_requirements(self, component: dict) -> list[dict]:
        """Generate functional requirements for a component."""
        return [
            {
                "id": f"FR-{component.get('name', 'UNKNOWN')}-001",
                "description": f"Implement {component.get('name')} component",
                "priority": "must",
            },
            {
                "id": f"FR-{component.get('name', 'UNKNOWN')}-002",
                "description": f"Add error handling for {component.get('name')}",
                "priority": "must",
            },
        ]

    def _generate_nfr(self, component: dict) -> list[dict]:
        """Generate non-functional requirements for a component."""
        return [
            {
                "category": "performance",
                "requirement": "Response time < 200ms",
            },
            {
                "category": "reliability",
                "requirement": "99.9% uptime",
            },
        ]

    def _generate_acceptance_criteria(self, component: dict) -> list[str]:
        """Generate acceptance criteria for a component."""
        return [
            f"{component.get('name')} renders correctly",
            f"{component.get('name')} handles errors gracefully",
            f"Unit tests pass for {component.get('name')}",
        ]

    def _generate_tasks_from_spec(
        self,
        spec: dict,
        start_order: int,
    ) -> list[dict]:
        """Generate tasks from a spec."""
        return [
            {
                "title": f"Implement {spec.get('component')} UI",
                "description": f"Create UI components for {spec.get('component')}",
                "type": "feature",
                "priority": spec.get("priority", "medium"),
                "estimated_hours": spec.get("estimated_hours", 4) // 2,
                "dependencies": [],
            },
            {
                "title": f"Implement {spec.get('component')} logic",
                "description": f"Add business logic for {spec.get('component')}",
                "type": "feature",
                "priority": spec.get("priority", "medium"),
                "estimated_hours": spec.get("estimated_hours", 4) // 2,
                "dependencies": [],
            },
            {
                "title": f"Add unit tests for {spec.get('component')}",
                "description": f"Write unit tests for {spec.get('component')}",
                "type": "test",
                "priority": "medium",
                "estimated_hours": 1,
                "dependencies": [],
            },
        ]

    def clear_all(self) -> None:
        """Clear all stored documents (for testing)."""
        self._store.clear()


# Global instance
openspec_service = OpenSpecService()
