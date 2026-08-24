package com.uccharan.app.data.remote

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

data class ListeningExercise(
    /** Never shown as text until after the learner answers — see [com.uccharan.app.ui.listening.ListeningScreen]'s doc on why. */
    val passage: String,
    val question: String,
    val options: List<String>,
    val correctOptionIndex: Int,
    val explanation: String,
)

/**
 * Talks to the FastAPI backend's `/api/v1/listening/generate` endpoint —
 * generates one round of listening-comprehension practice (a short passage
 * read aloud via on-device text-to-speech, plus a multiple-choice
 * comprehension question) around a topic. Same plain-OkHttp approach as
 * [CorrectionApi]/[PracticeApi], for the same reason.
 */
class ListeningApi(
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS) // Gemini calls + a cold Render free-tier start (can take the better part of a minute) can be slow
        .build(),
    private val baseUrl: String = BackendConfig.baseUrl,
    private val idTokenProvider: suspend () -> String? = { null },
) {
    suspend fun generateExercise(topic: String): Result<ListeningExercise> = withContext(Dispatchers.IO) {
        runCatching {
            val body = JSONObject().apply { put("topic", topic) }

            val requestBuilder = Request.Builder()
                .url("$baseUrl/api/v1/listening/generate")
                .post(body.toString().toRequestBody("application/json".toMediaType()))
            idTokenProvider()?.let { requestBuilder.addHeader("Authorization", "Bearer $it") }

            client.newCall(requestBuilder.build()).execute().use { response ->
                val responseBody = response.body?.string() ?: throw IOException("Empty response from server")
                if (response.code == 401) throw BackendAuthException("Server returned 401: $responseBody")
                if (!response.isSuccessful) throw IOException("Server returned ${response.code}: $responseBody")

                val json = JSONObject(responseBody)
                val optionsArray = json.getJSONArray("options")
                ListeningExercise(
                    passage = json.getString("passage"),
                    question = json.getString("question"),
                    options = (0 until optionsArray.length()).map { optionsArray.getString(it) },
                    correctOptionIndex = json.getInt("correct_option_index"),
                    explanation = json.getString("explanation"),
                )
            }
        }.withFriendlyBackendError()
    }
}
