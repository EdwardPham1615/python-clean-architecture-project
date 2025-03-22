from dependency_injector import containers, providers

from internal.infrastructures import InfrastructureContainer


class ServiceContainer(containers.DeclarativeContainer):
    """Manages the dependency injection of services."""

    wiring_config = containers.WiringConfiguration(modules=[__name__])

    infrastructures_ = providers.Container(InfrastructureContainer)
