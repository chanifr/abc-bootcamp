#!/usr/bin/env python3
"""Comprehensive database seeding script with Exercise 1 data."""

import asyncio
import sys
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.candidate import Candidate, CandidateStatus
from app.models.candidate_position import CandidatePosition
from app.models.document import Document, DocumentType
from app.models.education import Education
from app.models.experience import Experience
from app.models.position import Position, PositionStatus
from app.models.position_skill import PositionSkill
from app.models.skill import Skill, SkillLevel
from app.models.user import User, UserRole


async def create_users(session):
    """Create admin and test users."""
    print("Creating users...")

    # Check if admin exists
    result = await session.execute(select(User).where(User.email == "admin@hellio.com"))
    if result.scalar_one_or_none():
        print("  - Admin user already exists")
    else:
        admin = User(
            email="admin@hellio.com",
            hashed_password=hash_password("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(admin)
        print("  - Created admin user (admin@hellio.com / admin123)")

    # Create editor user
    result = await session.execute(select(User).where(User.email == "editor@hellio.com"))
    if not result.scalar_one_or_none():
        editor = User(
            email="editor@hellio.com",
            hashed_password=hash_password("editor123"),
            full_name="Editor User",
            role=UserRole.EDITOR,
            is_active=True,
        )
        session.add(editor)
        print("  - Created editor user (editor@hellio.com / editor123)")

    # Create read-only user
    result = await session.execute(select(User).where(User.email == "viewer@hellio.com"))
    if not result.scalar_one_or_none():
        viewer = User(
            email="viewer@hellio.com",
            hashed_password=hash_password("viewer123"),
            full_name="Read Only User",
            role=UserRole.READ_ONLY,
            is_active=True,
        )
        session.add(viewer)
        print("  - Created viewer user (viewer@hellio.com / viewer123)")

    await session.commit()


async def seed_candidates(session):
    """Seed candidates from Exercise 1 data."""
    print("\nSeeding candidates...")

    # Sarah Chen
    sarah = Candidate(
        name="Sarah Chen",
        email="sarah.chen@email.com",
        phone="+1-555-0123",
        location="San Francisco, CA",
        summary="Full-stack developer with 8 years of experience specializing in React and Node.js. Passionate about creating scalable web applications and mentoring junior developers.",
        status=CandidateStatus.ACTIVE,
        sort_order=1,
    )
    session.add(sarah)
    await session.flush()

    # Sarah's experiences
    experiences = [
        Experience(
            candidate_id=sarah.id,
            company="TechCorp Inc.",
            title="Senior Full-Stack Developer",
            start_date=date(2020, 3, 1),
            end_date=None,  # Current
            description="Lead developer for customer-facing web applications. Architected microservices backend and implemented CI/CD pipeline.",
        ),
        Experience(
            candidate_id=sarah.id,
            company="StartupXYZ",
            title="Full-Stack Developer",
            start_date=date(2017, 6, 1),
            end_date=date(2020, 2, 28),
            description="Developed and maintained multiple client projects using React, Node.js, and PostgreSQL.",
        ),
        Experience(
            candidate_id=sarah.id,
            company="WebSolutions Ltd",
            title="Junior Developer",
            start_date=date(2015, 8, 1),
            end_date=date(2017, 5, 31),
            description="Built responsive websites and assisted in full-stack development projects.",
        ),
    ]
    session.add_all(experiences)

    # Sarah's education
    sarah_edu = Education(
        candidate_id=sarah.id,
        institution="University of California, Berkeley",
        degree="Bachelor of Science",
        field="Computer Science",
        start_date=date(2011, 9, 1),
        end_date=date(2015, 5, 31),
    )
    session.add(sarah_edu)

    # Sarah's skills
    sarah_skills = [
        Skill(candidate_id=sarah.id, name="React", level=SkillLevel.EXPERT),
        Skill(candidate_id=sarah.id, name="Node.js", level=SkillLevel.EXPERT),
        Skill(candidate_id=sarah.id, name="TypeScript", level=SkillLevel.ADVANCED),
        Skill(candidate_id=sarah.id, name="PostgreSQL", level=SkillLevel.ADVANCED),
        Skill(candidate_id=sarah.id, name="Docker", level=SkillLevel.INTERMEDIATE),
    ]
    session.add_all(sarah_skills)

    # Sarah's document
    sarah_doc = Document(
        candidate_id=sarah.id,
        type=DocumentType.CV,
        name="Sarah_Chen_Resume.pdf",
        url="/storage/documents/sarah_chen_resume.pdf",
        uploaded_at=datetime.utcnow(),
    )
    session.add(sarah_doc)

    print("  - Created candidate: Sarah Chen")

    # Michael Rodriguez
    michael = Candidate(
        name="Michael Rodriguez",
        email="m.rodriguez@email.com",
        phone="+1-555-0124",
        location="Austin, TX",
        summary="DevOps engineer with strong background in cloud infrastructure and automation. Experienced in AWS, Kubernetes, and infrastructure as code.",
        status=CandidateStatus.ACTIVE,
        sort_order=2,
    )
    session.add(michael)
    await session.flush()

    # Michael's experiences
    michael_exp = [
        Experience(
            candidate_id=michael.id,
            company="CloudFirst Technologies",
            title="Senior DevOps Engineer",
            start_date=date(2019, 1, 1),
            end_date=None,  # Current
            description="Designed and implemented cloud infrastructure for multiple products. Reduced deployment time by 60% through automation.",
        ),
        Experience(
            candidate_id=michael.id,
            company="DataCorp",
            title="DevOps Engineer",
            start_date=date(2016, 7, 1),
            end_date=date(2018, 12, 31),
            description="Managed AWS infrastructure and implemented CI/CD pipelines using Jenkins and GitLab.",
        ),
    ]
    session.add_all(michael_exp)

    # Michael's education
    michael_edu = Education(
        candidate_id=michael.id,
        institution="Texas A&M University",
        degree="Bachelor of Science",
        field="Information Technology",
        start_date=date(2012, 9, 1),
        end_date=date(2016, 5, 31),
    )
    session.add(michael_edu)

    # Michael's skills
    michael_skills = [
        Skill(candidate_id=michael.id, name="AWS", level=SkillLevel.EXPERT),
        Skill(candidate_id=michael.id, name="Kubernetes", level=SkillLevel.ADVANCED),
        Skill(candidate_id=michael.id, name="Docker", level=SkillLevel.EXPERT),
        Skill(candidate_id=michael.id, name="Terraform", level=SkillLevel.ADVANCED),
        Skill(candidate_id=michael.id, name="Python", level=SkillLevel.INTERMEDIATE),
    ]
    session.add_all(michael_skills)

    # Michael's document
    michael_doc = Document(
        candidate_id=michael.id,
        type=DocumentType.CV,
        name="Michael_Rodriguez_CV.pdf",
        url="/storage/documents/michael_rodriguez_cv.pdf",
        uploaded_at=datetime.utcnow(),
    )
    session.add(michael_doc)

    print("  - Created candidate: Michael Rodriguez")

    # Emily Watson
    emily = Candidate(
        name="Emily Watson",
        email="emily.watson@email.com",
        phone="+1-555-0125",
        location="New York, NY",
        summary="Product Manager with 6 years of experience leading cross-functional teams. Strong technical background with focus on user-centric design and agile methodologies.",
        status=CandidateStatus.ACTIVE,
        sort_order=3,
    )
    session.add(emily)
    await session.flush()

    # Emily's experiences
    emily_exp = [
        Experience(
            candidate_id=emily.id,
            company="ProductTech Inc.",
            title="Senior Product Manager",
            start_date=date(2020, 6, 1),
            end_date=None,  # Current
            description="Lead product strategy for B2B SaaS platform. Increased user engagement by 40% through data-driven feature prioritization.",
        ),
        Experience(
            candidate_id=emily.id,
            company="InnovateLab",
            title="Product Manager",
            start_date=date(2018, 3, 1),
            end_date=date(2020, 5, 31),
            description="Managed product roadmap for mobile application. Coordinated with engineering and design teams.",
        ),
        Experience(
            candidate_id=emily.id,
            company="TechStartup",
            title="Associate Product Manager",
            start_date=date(2017, 1, 1),
            end_date=date(2018, 2, 28),
            description="Assisted in product development and user research activities.",
        ),
    ]
    session.add_all(emily_exp)

    # Emily's education
    emily_edu = [
        Education(
            candidate_id=emily.id,
            institution="Columbia University",
            degree="Master of Business Administration",
            field="Technology Management",
            start_date=date(2015, 9, 1),
            end_date=date(2017, 5, 31),
        ),
        Education(
            candidate_id=emily.id,
            institution="MIT",
            degree="Bachelor of Science",
            field="Computer Science",
            start_date=date(2011, 9, 1),
            end_date=date(2015, 5, 31),
        ),
    ]
    session.add_all(emily_edu)

    # Emily's skills
    emily_skills = [
        Skill(candidate_id=emily.id, name="Product Management", level=SkillLevel.EXPERT),
        Skill(candidate_id=emily.id, name="Agile/Scrum", level=SkillLevel.EXPERT),
        Skill(candidate_id=emily.id, name="User Research", level=SkillLevel.ADVANCED),
        Skill(candidate_id=emily.id, name="SQL", level=SkillLevel.INTERMEDIATE),
        Skill(candidate_id=emily.id, name="Python", level=SkillLevel.BEGINNER),
    ]
    session.add_all(emily_skills)

    # Emily's document
    emily_doc = Document(
        candidate_id=emily.id,
        type=DocumentType.CV,
        name="Emily_Watson_Resume.pdf",
        url="/storage/documents/emily_watson_resume.pdf",
        uploaded_at=datetime.utcnow(),
    )
    session.add(emily_doc)

    print("  - Created candidate: Emily Watson")

    await session.commit()
    return sarah, michael, emily


async def seed_positions(session):
    """Seed positions from Exercise 1 data."""
    print("\nSeeding positions...")

    # Senior Full-Stack Developer
    fullstack = Position(
        title="Senior Full-Stack Developer",
        department="Engineering",
        location="San Francisco, CA (Hybrid)",
        description="We are seeking an experienced Full-Stack Developer to join our engineering team. You will work on building scalable web applications using modern technologies and collaborate with cross-functional teams to deliver high-quality products.",
        requirements="5+ years of experience in full-stack development. Strong proficiency in React, Node.js, and database design. Experience with cloud platforms (AWS/GCP). Excellent problem-solving skills and ability to work in an agile environment.",
        min_experience_years=5,
        status=PositionStatus.OPEN,
        posted_date=date(2024, 1, 15),
        sort_order=1,
    )
    session.add(fullstack)
    await session.flush()

    # Required skills
    fullstack_skills = [
        PositionSkill(position_id=fullstack.id, name="React"),
        PositionSkill(position_id=fullstack.id, name="Node.js"),
        PositionSkill(position_id=fullstack.id, name="TypeScript"),
        PositionSkill(position_id=fullstack.id, name="PostgreSQL"),
        PositionSkill(position_id=fullstack.id, name="AWS"),
    ]
    session.add_all(fullstack_skills)

    print("  - Created position: Senior Full-Stack Developer")

    # DevOps Engineer
    devops = Position(
        title="DevOps Engineer",
        department="Infrastructure",
        location="Remote",
        description="Join our infrastructure team to build and maintain our cloud platform. You will automate deployment processes, ensure system reliability, and implement security best practices.",
        requirements="3+ years of DevOps experience. Strong knowledge of AWS/Azure, Kubernetes, and CI/CD tools. Experience with infrastructure as code (Terraform/CloudFormation). Strong scripting skills in Python or Bash.",
        min_experience_years=3,
        status=PositionStatus.OPEN,
        posted_date=date(2024, 1, 20),
        sort_order=2,
    )
    session.add(devops)
    await session.flush()

    # Required skills
    devops_skills = [
        PositionSkill(position_id=devops.id, name="AWS"),
        PositionSkill(position_id=devops.id, name="Kubernetes"),
        PositionSkill(position_id=devops.id, name="Docker"),
        PositionSkill(position_id=devops.id, name="Terraform"),
        PositionSkill(position_id=devops.id, name="Python"),
    ]
    session.add_all(devops_skills)

    print("  - Created position: DevOps Engineer")

    # Product Manager
    pm = Position(
        title="Product Manager - B2B SaaS",
        department="Product",
        location="New York, NY (Hybrid)",
        description="We are looking for a Product Manager to drive our B2B SaaS product strategy. You will define product vision, prioritize features, and work closely with engineering and design teams to deliver value to our customers.",
        requirements="4+ years of product management experience, preferably in B2B SaaS. Strong analytical and communication skills. Experience with agile methodologies. Technical background is a plus. MBA preferred but not required.",
        min_experience_years=4,
        status=PositionStatus.OPEN,
        posted_date=date(2024, 1, 25),
        sort_order=3,
    )
    session.add(pm)
    await session.flush()

    # Required skills
    pm_skills = [
        PositionSkill(position_id=pm.id, name="Product Management"),
        PositionSkill(position_id=pm.id, name="Agile/Scrum"),
        PositionSkill(position_id=pm.id, name="User Research"),
        PositionSkill(position_id=pm.id, name="SQL"),
    ]
    session.add_all(pm_skills)

    print("  - Created position: Product Manager - B2B SaaS")

    await session.commit()
    return fullstack, devops, pm


async def create_relationships(session, candidates, positions):
    """Create candidate-position relationships."""
    print("\nCreating candidate-position relationships...")

    sarah, michael, emily = candidates
    fullstack, devops, pm = positions

    # Sarah applied to Full-Stack Developer
    link1 = CandidatePosition(candidate_id=sarah.id, position_id=fullstack.id)
    session.add(link1)
    print(f"  - Sarah Chen -> Senior Full-Stack Developer")

    # Michael applied to DevOps Engineer
    link2 = CandidatePosition(candidate_id=michael.id, position_id=devops.id)
    session.add(link2)
    print(f"  - Michael Rodriguez -> DevOps Engineer")

    # Emily applied to Product Manager
    link3 = CandidatePosition(candidate_id=emily.id, position_id=pm.id)
    session.add(link3)
    print(f"  - Emily Watson -> Product Manager - B2B SaaS")

    # Sarah also applied to DevOps (cross-apply)
    link4 = CandidatePosition(candidate_id=sarah.id, position_id=devops.id)
    session.add(link4)
    print(f"  - Sarah Chen -> DevOps Engineer")

    await session.commit()


async def main():
    """Main seeding function."""
    print("=" * 60)
    print("Hellio HR Database Seeding Script")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            # Create users
            await create_users(session)

            # Seed candidates
            candidates = await seed_candidates(session)

            # Seed positions
            positions = await seed_positions(session)

            # Create relationships
            await create_relationships(session, candidates, positions)

            print("\n" + "=" * 60)
            print("Database seeded successfully!")
            print("=" * 60)
            print("\nLogin credentials:")
            print("  Admin:  admin@hellio.com / admin123")
            print("  Editor: editor@hellio.com / editor123")
            print("  Viewer: viewer@hellio.com / viewer123")
            print("\nData summary:")
            print("  - 3 candidates (Sarah Chen, Michael Rodriguez, Emily Watson)")
            print("  - 3 positions (Full-Stack Dev, DevOps, Product Manager)")
            print("  - 4 candidate-position relationships")
            print("\nAPI available at: http://localhost:8000")
            print("API docs at: http://localhost:8000/api/v1/docs")
            print("=" * 60)

        except Exception as e:
            print(f"\nError seeding database: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
