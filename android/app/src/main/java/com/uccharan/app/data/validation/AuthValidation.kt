package com.uccharan.app.data.validation

/**
 * A plain regex rather than android.util.Patterns.EMAIL_ADDRESS: that field
 * is null under plain JVM unit tests (no real Android runtime backs it,
 * and this module intentionally has no Robolectric dependency), and it's
 * more permissive than we need. Good enough for "does this look like an
 * email" — Firebase does the real validation server-side regardless.
 */
private val EMAIL_REGEX = Regex("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$")

fun isValidEmail(email: String): Boolean = email.isNotBlank() && EMAIL_REGEX.matches(email)

data class PasswordRequirement(val label: String, val isMet: (String) -> Boolean)

/** Password policy: 8+ characters, at least one uppercase, one lowercase, one special character. */
val PASSWORD_REQUIREMENTS: List<PasswordRequirement> = listOf(
    PasswordRequirement("At least 8 characters") { it.length >= 8 },
    PasswordRequirement("One uppercase letter") { it.any(Char::isUpperCase) },
    PasswordRequirement("One lowercase letter") { it.any(Char::isLowerCase) },
    PasswordRequirement("One special character") { password -> password.any { !it.isLetterOrDigit() } },
)

fun unmetPasswordRequirements(password: String): List<PasswordRequirement> =
    PASSWORD_REQUIREMENTS.filterNot { it.isMet(password) }

fun isPasswordValid(password: String): Boolean = unmetPasswordRequirements(password).isEmpty()
