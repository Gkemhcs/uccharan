package com.uccharan.app.data.remote

import kotlinx.coroutines.test.runTest
import mockwebserver3.MockResponse
import mockwebserver3.MockWebServer
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

class ListeningApiTest {
    private lateinit var server: MockWebServer
    private lateinit var api: ListeningApi

    @Before
    fun setUp() {
        server = MockWebServer()
        server.start()
        api = ListeningApi(baseUrl = server.url("/").toString().removeSuffix("/"))
    }

    @After
    fun tearDown() {
        server.close()
    }

    @Test
    fun `sends the topic and parses a successful response`() = runTest {
        server.enqueue(
            MockResponse(
                body = """{
                    "passage": "Hi, table for two please.",
                    "question": "What did the speaker ask for?",
                    "options": ["A table for two", "The bill", "A menu", "Directions"],
                    "correct_option_index": 0,
                    "explanation": "They said 'table for two'."
                }""",
            ),
        )

        val result = api.generateExercise("Ordering food at a restaurant").getOrThrow()

        val request = server.takeRequest()
        assertEquals("POST", request.method)
        assertTrue(request.body!!.utf8().contains("\"topic\":\"Ordering food at a restaurant\""))
        assertEquals("Hi, table for two please.", result.passage)
        assertEquals(4, result.options.size)
        assertEquals(0, result.correctOptionIndex)
    }

    @Test
    fun `treats a non-2xx response as a failure instead of throwing`() = runTest {
        server.enqueue(MockResponse(code = 500, body = "internal error"))

        val result = api.generateExercise("Ordering food")

        assertTrue(result.isFailure)
    }

    @Test
    fun `attaches the id token as a bearer authorization header when one is available`() = runTest {
        val authedApi = ListeningApi(baseUrl = server.url("/").toString().removeSuffix("/"), idTokenProvider = { "a-firebase-id-token" })
        server.enqueue(
            MockResponse(body = """{"passage": "p", "question": "q", "options": ["a", "b"], "correct_option_index": 0, "explanation": "e"}"""),
        )

        authedApi.generateExercise("Ordering food")

        val request = server.takeRequest()
        assertEquals("Bearer a-firebase-id-token", request.headers["Authorization"])
    }

    @Test
    fun `a 401 response is a distinguishable auth failure, not a generic connection error`() = runTest {
        server.enqueue(MockResponse(code = 401, body = """{"detail": "Invalid or expired session"}"""))

        val result = api.generateExercise("Ordering food")

        assertTrue(result.isFailure)
        assertTrue(result.exceptionOrNull()?.cause is BackendAuthException)
    }
}
