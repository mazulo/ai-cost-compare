from ai_cost_compare.providers.base import UsageProvider
from ai_cost_compare.providers.claude import provider as claude_provider

_REGISTRY: dict[str, UsageProvider] = {
    claude_provider.id: claude_provider,
}


def get(provider_id: str) -> UsageProvider:
    try:
        return _REGISTRY[provider_id]
    except KeyError as exc:
        known = ", ".join(sorted(_REGISTRY))
        raise KeyError(f"Unknown provider {provider_id!r}. Choose from: {known}") from exc


def list_ids() -> list[str]:
    return sorted(_REGISTRY)
