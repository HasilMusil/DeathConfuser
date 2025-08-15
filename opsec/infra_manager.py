"""Temporary infrastructure manager used for OPSEC testing.

This module simulates the creation of throwaway infrastructure used for
callbacks or staging servers. It does not actually allocate resources
but mimics an API call to a VPS provider so the rest of the framework
can operate as if real infrastructure were provisioned.
"""
from __future__ import annotations

import asyncio
import random
import uuid
from dataclasses import dataclass
from typing import Optional

from ..core.logger import get_logger


@dataclass
class Infra:
    domain: str
    ip: str


class InfraManager:
    """Simulate provisioning of disposable infrastructure."""

    def __init__(self) -> None:
        self.current: Optional[Infra] = None
        self.log = get_logger(__name__)

    async def provision(self) -> Infra:
        """Provision a temporary VPS and DNS record (simulated)."""
        domain = f"{uuid.uuid4().hex}.infra.example.com"
        ip = f"192.0.2.{random.randint(2, 254)}"
        self.current = Infra(domain=domain, ip=ip)
        self.log.info("Provisioned temporary infra %s (%s)", domain, ip)
        # Simulate an external API call latency
        await asyncio.sleep(0.5)
        return self.current

    async def register_domain(self, base: str = "example.com") -> str:
        """Register a fake domain for callbacks."""
        sub = uuid.uuid4().hex
        domain = f"{sub}.{base}"
        self.log.debug("Registered domain %s", domain)
        return domain

    async def deploy_callback(self, service: str = "http") -> str:
        """Simulate deployment of a callback service (e.g. Interactsh)."""
        if not self.current:
            await self.provision()
        await asyncio.sleep(0.2)
        endpoint = f"{service}://{self.current.domain}"
        self.log.info("Deployed %s callback at %s", service, endpoint)
        return endpoint

    async def teardown(self) -> None:
        """Tear down the simulated infrastructure."""
        if not self.current:
            return
        self.log.info("Tearing down infra %s", self.current.domain)
        await asyncio.sleep(0.2)
        self.current = None

    async def generate_burner_identity(self) -> dict:
        """Generate a disposable identity for publishing."""
        name = f"user-{uuid.uuid4().hex[:6]}"
        domain = random.choice([
            "mailinator.com",
            "example.net",
            "tempmail.com",
        ])
        email = f"{name}@{domain}"
        user_agent = random.choice([
            "Mozilla/5.0", "curl/7.88.1", "Wget/1.21.1",
        ])
        version = f"0.{random.randint(0,9)}.{random.randint(0,9)}"
        delay = random.uniform(0.5, 2.0)
        await asyncio.sleep(0)  # allow scheduling
        return {
            "name": name,
            "email": email,
            "user_agent": user_agent,
            "version": version,
            "delay": delay,
        }
