package com.uccharan.app.data.validation

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AuthValidationTest {

    @Test
    fun `valid emails pass, malformed ones fail`() {
        assertTrue(isValidEmail("student@example.com"))
        assertTrue(isValidEmail("a.b+tag@sub.example.co.in"))

        assertFalse(isValidEmail(""))
        assertFalse(isValidEmail("   "))
        assertFalse(isValidEmail("not-an-email"))
        assertFalse(isValidEmail("missing-domain@"))
        assertFalse(isValidEmail("@missing-local.com"))
        assertFalse(isValidEmail("no-at-sign.com"))
    }

    @Test
    fun `password needs length, case mix, and a special character`() {
        assertFalse(isPasswordValid("short1!"))
        assertFalse(isPasswordValid("alllowercase1!"))
        assertFalse(isPasswordValid("ALLUPPERCASE1!"))
        assertFalse(isPasswordValid("NoSpecialChar1"))

        assertTrue(isPasswordValid("Valid1Pass!"))
    }

    @Test
    fun `unmet requirements lists exactly what's missing`() {
        val unmet = unmetPasswordRequirements("alllowercase")

        assertEquals(
            setOf("One uppercase letter", "One special character"),
            unmet.map { it.label }.toSet(),
        )
    }
}
