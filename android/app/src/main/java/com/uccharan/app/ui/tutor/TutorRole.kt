package com.uccharan.app.ui.tutor

/**
 * The "costume" a practice topic implies — shared by [TutorCharacter] (which
 * draws a matching accessory on the tutor) and `SceneBanner` (which shows a
 * matching emoji badge), so the two always agree on what scene a topic maps
 * to. Matched once per topic via simple keyword search — cheap, deterministic,
 * no network/AI call needed to pick a costume.
 */
enum class TutorRole(val emoji: String, val label: String, val keywords: List<String>) {
    AUTO("🛺", "On the Road", listOf("auto", "rickshaw", "taxi", "fare", "cab", "driver")),
    RESTAURANT("🍽️", "At the Table", listOf("restaurant", "food", "order", "waiter", "dinner", "cafe", "café", "meal", "eat")),
    MEDICAL("🩺", "At the Clinic", listOf("doctor", "symptom", "medicine", "pharmacy", "hospital", "health", "sick", "clinic")),
    SHOP("🛍️", "At the Shop", listOf("shop", "market", "buy", "price", "discount", "grocery", "vendor", "store", "bargain")),
    DIRECTIONS("🧭", "On the Street", listOf("direction", "street", "road", "station", "stranger", "walk", "lost", "corner")),
    OFFICE("💼", "At Work", listOf("interview", "job", "colleague", "meeting", "office", "professional", "work", "career", "present")),
    HOME("🏠", "At Home", listOf("family", "home", "neighbor", "household", "relative", "gathering")),
    PHONE("📞", "On a Call", listOf("phone", "call", "message", "video")),
    TRAVEL("✈️", "Traveling", listOf("hotel", "ticket", "travel", "booking", "trip", "flight", "train", "airport", "journey")),
    TEACHER("💬", "Your Tutor", emptyList()),
    ;

    companion object {
        fun forTopic(topic: String): TutorRole {
            val lower = topic.lowercase()
            return entries.firstOrNull { role -> role.keywords.any { keyword -> lower.contains(keyword) } } ?: TEACHER
        }
    }
}
