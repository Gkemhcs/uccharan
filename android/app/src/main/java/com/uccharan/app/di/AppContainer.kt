package com.uccharan.app.di

import com.uccharan.app.data.remote.CorrectionApi
import com.uccharan.app.data.remote.ListeningApi
import com.uccharan.app.data.remote.PracticeApi
import com.uccharan.app.data.repository.AuthRepository
import com.uccharan.app.data.repository.LessonRepository
import com.uccharan.app.data.repository.QuizRepository
import com.uccharan.app.data.repository.UserProfileRepository

/**
 * Manual dependency injection — deliberately not Hilt. This app has a small,
 * flat dependency graph (a handful of singletons, no scoping complexity), so
 * a plain container avoids an annotation-processing build plugin for no real
 * benefit at this size. Revisit if the graph grows enough to need real scoping.
 */
class AppContainer {
    val authRepository: AuthRepository by lazy { AuthRepository() }
    val userProfileRepository: UserProfileRepository by lazy { UserProfileRepository() }
    val lessonRepository: LessonRepository by lazy { LessonRepository() }
    val quizRepository: QuizRepository by lazy { QuizRepository() }
    // Both APIs need a fresh Firebase ID token per call — the backend rejects
    // /correct and /practice/* requests without one (see backend app/core/auth.py).
    val correctionApi: CorrectionApi by lazy { CorrectionApi(idTokenProvider = { authRepository.getIdToken() }) }
    val practiceApi: PracticeApi by lazy { PracticeApi(idTokenProvider = { authRepository.getIdToken() }) }
    val listeningApi: ListeningApi by lazy { ListeningApi(idTokenProvider = { authRepository.getIdToken() }) }
}
