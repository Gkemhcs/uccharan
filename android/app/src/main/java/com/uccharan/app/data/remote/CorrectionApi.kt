package com.uccharan.app.data.remote

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
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
        .readTimeout(60, TimeUnit.SECONDS) // Gemini calls + a cold Render free-tier start (can take the better part of a minute) can be slow
        .build(),
    private val baseUrl: String = BackendConfig.baseUrl,
    /** Supplies a fresh Firebase ID token per call, attached as `Authorization: Bearer <token>` — the backend rejects any request without one. Defaults to no token, since tests exercising the request/response shape don't need auth wired up. */
    private val idTokenProvider: suspend () -> String? = { null },
) {
    suspend fun correctAttempt(
        targetSentence: String,
        spokenText: String,
        preferredAddressTerm: String?,
        nativeLanguage: String?,
        focusSounds: List<String> = emptyList(),
    ): Result<CorrectionResult> = withContext(Dispatchers.IO) {
        runCatching {
            val body = JSONObject().apply {
                put("target_sentence", targetSentence)
                put("spoken_text", spokenText)
                preferredAddressTerm?.let { put("preferred_address_term", it) }
                nativeLanguage?.let { put("native_language", it) }
                if (focusSounds.isNotEmpty()) put("focus_sounds", JSONArray(focusSounds))
            }

            val requestBuilder = Request.Builder()
                .url("$baseUrl/api/v1/correct")
                .post(body.toString().toRequestBody("application/json".toMediaType()))
            idTokenProvider()?.let { requestBuilder.addHeader("Authorization", "Bearer $it") }

            client.newCall(requestBuilder.build()).execute().use { response ->
                val responseBody = response.body?.string()
                    ?: throw IOException("Empty response from server")

                if (response.code == 401) {
                    throw BackendAuthException("Server returned 401: $responseBody")
                }
                if (!response.isSuccessful) {
                    throw IOException("Server returned ${response.code}: $responseBody")
                }

                val json = JSONObject(responseBody)
                CorrectionResult(
                    isCorrect = json.getBoolean("is_correct"),
                    feedback = json.getString("feedback"),
                    nativeExplanation = json.optNullableString("native_explanation"),
                )
            }
        }.withFriendlyBackendError()
    }

    /**
     * `optString(key, "")` is NOT a safe way to read a nullable field: when
     * the JSON value is explicitly `null` (which `native_explanation: str |
     * None = None` serializes to whenever it's unset, e.g. no native
     * language on the profile), org.json's `optString` returns the literal
     * 4-character string `"null"` instead of the empty-string fallback,
     * since it calls `.toString()` on the JSONObject.NULL sentinel rather
     * than treating it as absent — the same bug confirmed live in
     * `PracticeApi`'s correction bubble ("💡 null"). `isNull(key)` is the
     * actual correct way to detect both a missing key and an explicit null.
     */
    private fun JSONObject.optNullableString(key: String): String? {
        if (isNull(key)) return null
        return optString(key, "").ifEmpty { null }
    }
}
