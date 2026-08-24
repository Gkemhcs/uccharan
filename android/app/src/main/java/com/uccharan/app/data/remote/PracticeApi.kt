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

/** `speaker` is either "learner" or "tutor" — mirrors the backend's `PracticeMessage.speaker` Literal. */
data class PracticeMessage(
    val speaker: String,
    val text: String,
)

data class PracticeTurnResult(
    val tutorReply: String,
    val correction: String?,
    val nativeNote: String?,
    /**
     * Carried conversation-memory state — see [PracticeConversationViewModel]'s
     * class doc. The caller's only job is to store these two values and echo
     * them back unchanged on the next [PracticeApi.sendTurn] call; the
     * backend alone decides when/how to update them.
     */
    val conversationSummary: String?,
    val summarizedThroughIndex: Int,
)

/**
 * Talks to the FastAPI backend's practice endpoints (under `/api/v1/practice`)
 * — "Practice with your Tutor", a roleplay conversation mode distinct from
 * the fixed speak_repeat lessons [CorrectionApi] serves. Same plain-OkHttp
 * approach as [CorrectionApi], for the same reason: one small hand-written
 * client per backend feature area is less moving parts than a code-generated one.
 */
class PracticeApi(
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS) // Gemini calls + a cold Render free-tier start (can take the better part of a minute) can be slow
        .build(),
    private val baseUrl: String = BackendConfig.baseUrl,
    /** Supplies a fresh Firebase ID token per call, attached as `Authorization: Bearer <token>` — the backend rejects any request without one. Defaults to no token, since tests exercising the request/response shape don't need auth wired up. */
    private val idTokenProvider: suspend () -> String? = { null },
) {
    suspend fun sendTurn(
        chatId: String,
        topic: String,
        history: List<PracticeMessage>,
        learnerMessage: String,
        preferredAddressTerm: String?,
        nativeLanguage: String?,
        conversationSummary: String? = null,
        summarizedThroughIndex: Int = 0,
    ): Result<PracticeTurnResult> = withContext(Dispatchers.IO) {
        runCatching {
            val body = JSONObject().apply {
                put("chat_id", chatId)
                put("topic", topic)
                put("history", history.toJsonArray())
                put("learner_message", learnerMessage)
                preferredAddressTerm?.let { put("preferred_address_term", it) }
                nativeLanguage?.let { put("native_language", it) }
                conversationSummary?.let { put("conversation_summary", it) }
                put("summarized_through_index", summarizedThroughIndex)
            }

            val requestBuilder = Request.Builder()
                .url("$baseUrl/api/v1/practice/turn")
                .post(body.toString().toRequestBody("application/json".toMediaType()))
            idTokenProvider()?.let { requestBuilder.addHeader("Authorization", "Bearer $it") }

            client.newCall(requestBuilder.build()).execute().use { response ->
                val responseBody = response.body?.string() ?: throw IOException("Empty response from server")
                if (response.code == 401) throw BackendAuthException("Server returned 401: $responseBody")
                if (!response.isSuccessful) throw IOException("Server returned ${response.code}: $responseBody")

                val json = JSONObject(responseBody)
                PracticeTurnResult(
                    tutorReply = json.getString("tutor_reply"),
                    correction = json.optNullableString("correction"),
                    nativeNote = json.optNullableString("native_note"),
                    conversationSummary = json.optNullableString("conversation_summary"),
                    summarizedThroughIndex = json.optInt("summarized_through_index", 0),
                )
            }
        }.withFriendlyBackendError()
    }

    /**
     * Compresses conversation turns into a short durable-facts note — the
     * same operation [sendTurn] triggers automatically server-side once a
     * conversation grows long, exposed standalone in case it's independently
     * useful later (e.g. showing a session summary). Not called by
     * [PracticeConversationViewModel] today — see its class doc.
     */
    suspend fun summarize(
        history: List<PracticeMessage>,
        previousSummary: String?,
    ): Result<String> = withContext(Dispatchers.IO) {
        runCatching {
            val body = JSONObject().apply {
                put("history", history.toJsonArray())
                previousSummary?.let { put("previous_summary", it) }
            }

            val requestBuilder = Request.Builder()
                .url("$baseUrl/api/v1/practice/summarize")
                .post(body.toString().toRequestBody("application/json".toMediaType()))
            idTokenProvider()?.let { requestBuilder.addHeader("Authorization", "Bearer $it") }

            client.newCall(requestBuilder.build()).execute().use { response ->
                val responseBody = response.body?.string() ?: throw IOException("Empty response from server")
                if (response.code == 401) throw BackendAuthException("Server returned 401: $responseBody")
                if (!response.isSuccessful) throw IOException("Server returned ${response.code}: $responseBody")
                JSONObject(responseBody).getString("summary")
            }
        }.withFriendlyBackendError()
    }

    private fun List<PracticeMessage>.toJsonArray(): JSONArray = JSONArray().apply {
        forEach { message -> put(JSONObject().apply { put("speaker", message.speaker); put("text", message.text) }) }
    }

    /**
     * `optString(key, "")` is NOT a safe way to read a nullable field: when
     * the JSON value is explicitly `null` (which every `x: str | None = None`
     * Pydantic field serializes to whenever it's unset — e.g. `correction`
     * on a turn with no correction to flag), org.json's `optString` returns
     * the literal 4-character string `"null"` instead of the empty-string
     * fallback, since it calls `.toString()` on the JSONObject.NULL sentinel
     * rather than treating it as absent. That shipped as a real bug here —
     * confirmed live: the correction bubble displayed "💡 null" whenever the
     * tutor had nothing to correct. `isNull(key)` is the actual correct way
     * to detect both a missing key and an explicit JSON null.
     */
    private fun JSONObject.optNullableString(key: String): String? {
        if (isNull(key)) return null
        return optString(key, "").ifEmpty { null }
    }
}
