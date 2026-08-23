package com.uccharan.app.data.remote

import kotlinx.coroutines.test.runTest
import mockwebserver3.MockResponse
import mockwebserver3.MockWebServer
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

class CorrectionApiTest {
    private lateinit var server: MockWebServer
    private lateinit var api: CorrectionApi

    @Before
    fun setUp() {
        server = MockWebServer()
        server.start()
        api = CorrectionApi(baseUrl = server.url("/").toString().removeSuffix("/"))
    }

    @After
    fun tearDown() {
        server.close()
    }

    @Test
    fun `sends target sentence, spoken text, and optional preferences as JSON`() = runTest {
        server.enqueue(MockResponse(body = """{"is_correct": true, "feedback": "Nice!", "native_explanation": null}"""))

        api.correctAttempt("Hi.", "Hi.", "Nanna", "Telugu")

        val request = server.takeRequest()
        val body = request.body!!.utf8()
        assertEquals("POST", request.method)
        assertTrue(body.contains("\"target_sentence\":\"Hi.\""))
        assertTrue(body.contains("\"preferred_address_term\":\"Nanna\""))
        assertTrue(body.contains("\"native_language\":\"Telugu\""))
    }

    @Test
    fun `omits optional fields when preferences aren't set`() = runTest {
        server.enqueue(MockResponse(body = """{"is_correct": true, "feedback": "Nice!", "native_explanation": null}"""))

        api.correctAttempt("Hi.", "Hi.", null, null)

        val body = server.takeRequest().body!!.utf8()
        assertTrue(!body.contains("preferred_address_term"))
        assertTrue(!body.contains("native_language"))
    }

    @Test
    fun `parses a successful response including a null native explanation`() = runTest {
        server.enqueue(MockResponse(body = """{"is_correct": false, "feedback": "Try again", "native_explanation": null}"""))

        val result = api.correctAttempt("Hi.", "Hey.", null, null).getOrThrow()

        assertEquals(false, result.isCorrect)
        assertEquals("Try again", result.feedback)
        assertEquals(null, result.nativeExplanation)
    }

    @Test
    fun `parses a native explanation when present`() = runTest {
        server.enqueue(
            MockResponse(body = """{"is_correct": false, "feedback": "Try again", "native_explanation": "Malli try cheyu"}"""),
        )

        val result = api.correctAttempt("Hi.", "Hey.", null, "Telugu").getOrThrow()

        assertEquals("Malli try cheyu", result.nativeExplanation)
    }

    @Test
    fun `treats a non-2xx response as a failure instead of throwing`() = runTest {
        server.enqueue(MockResponse(code = 500, body = "internal error"))

        val result = api.correctAttempt("Hi.", "Hi.", null, null)

        assertTrue(result.isFailure)
    }
}
