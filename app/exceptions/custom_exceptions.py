class ApplicationError(Exception):
    status_code = 500
    code = "internal_error"
    message = "An unexpected internal error occurred."


class ConfigurationError(ApplicationError):
    status_code = 503
    code = "ai_not_configured"
    message = "Configure AI_API_URL and AI_MODEL to enable analysis."


class ProviderError(ApplicationError):
    status_code = 502
    code = "provider_error"
    message = "The AI provider could not complete the request."


class NetworkError(ProviderError):
    code = "provider_network_error"
    message = "The AI provider could not be reached."


class ProviderTimeout(ApplicationError):
    status_code = 504
    code = "provider_timeout"
    message = "The AI provider timed out. Please try again later."


class InvalidAIResponse(ProviderError):
    code = "invalid_ai_response"
    message = "The AI provider returned an invalid analysis."
