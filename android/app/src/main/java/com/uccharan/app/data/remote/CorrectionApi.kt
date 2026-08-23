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

data class CorrectionResult(
    val isCorrect: Boolean,
    val feedback: String,
    val nativeExplanation: String?,
)

/**
 * Talks to the FastAPI backend's `/api/v1/correct` endpoint.
 *
 * Deliberately plain OkHttp + org.json instead of Retrofit — this app makes
 * exactly one kind of backend call, so a small hand-written client is less
 * moving parts than a code-generated one, and there's nothing in it a Retrofit
 * interface would meaningfully simplify.
 */
class CorrectionApi(
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS) // Gemini calls + a cold Render free-tier start can be slow
        .build(),
    private val baseUrl: String = BackendConfig.baseUrl,
) {
    suspend fun correctAttempt(
        targetSentence: String,
        spokenText: String,
        preferredAddressTerm: String?,
        nativeLanguage: String?,
    ): Result<CorrectionResult> = withContext(Dispatchers.IO) {
        runCatching {
            val body = JSONObject().apply {
                put("target_sentence", targetSentence)
                put("spoken_text", spokenText)
                preferredAddressTerm?.let { put("preferred_address_term", it) }
                nativeLanguage?.let { put("native_language", it) }
            }

            val request = Request.Builder()
                .url("$baseUrl/api/v1/correct")
                .post(body.toString().toRequestBody("application/json".toMediaType()))
                .build()

            client.newCall(request).execute().use { response ->
                val responseBody = response.body?.string()
                    ?: throw IOException("Empty response from server")

                if (!response.isSuccessful) {
                    throw IOException("Server returned ${response.code}: $responseBody")
                }

                val json = JSONObject(responseBody)
                CorrectionResult(
                    isCorrect = json.getBoolean("is_correct"),
                    feedback = json.getString("feedback"),
                    nativeExplanation = json.optString("native_explanation", "").ifEmpty { null },
                )
            }
        }
    }
}
