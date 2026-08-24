package com.uccharan.app.ui.navigation

import android.net.Uri
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.home.HomeScreen
import com.uccharan.app.ui.lesson.LessonScreen
import com.uccharan.app.ui.onboarding.OnboardingScreen
import com.uccharan.app.ui.practice.PracticeConversationScreen
import com.uccharan.app.ui.practice.PracticeScenarioPickerScreen
import com.uccharan.app.ui.profile.ProfileScreen
import com.uccharan.app.ui.quiz.QuizScreen
import com.uccharan.app.ui.roadmap.RoadmapOverviewScreen
import com.uccharan.app.ui.signin.SignInScreen

private object Routes {
    const val SIGN_IN = "sign_in"
    const val ONBOARDING = "onboarding"
    const val HOME = "home"
    const val PROFILE = "profile"
    const val LESSON = "lesson/{lessonId}"
    const val QUIZ = "quiz/{quizId}"
    const val PRACTICE_CONVERSATION = "practice/{topic}"
    const val PRACTICE_SCENARIO_PICKER = "practice_scenario_picker"
    const val ROADMAP_OVERVIEW = "roadmap_overview"
    fun lesson(lessonId: String) = "lesson/$lessonId"
    fun quiz(quizId: String) = "quiz/$quizId"

    // A day theme is free text ("Food & Ordering (Week 1 review)") — Uri.encode it going into
    // the route so characters like spaces/&/() don't collide with route segment syntax.
    // Navigation-Compose decodes path-template args automatically on the way out (matching
    // Uri.encode's escaping), so the composable below reads the plain decoded string back
    // directly — no manual decode call needed (and java.net.URLEncoder/URLDecoder must NOT be
    // used here instead: they're x-www-form-urlencoded, which encodes a space as '+' rather
    // than '%20' — Navigation's Uri-based decoding leaves a literal '+' as '+', not a space).
    fun practiceConversation(topic: String) = "practice/${Uri.encode(topic)}"
}

@Composable
fun UccharanNavHost(navController: NavHostController = rememberNavController()) {
    val container = LocalAppContainer.current
    val rootViewModel = uccharanViewModel { RootViewModel(container.authRepository, container.userProfileRepository) }
    val startState by rootViewModel.startState.collectAsState()

    // Drive top-level navigation from auth/onboarding state rather than
    // screens navigating themselves — a screen shouldn't need to know what
    // comes after it.
    LaunchedEffect(startState) {
        val currentRoute = navController.currentBackStackEntry?.destination?.route
        when (startState) {
            AppStartState.NeedsSignIn -> if (currentRoute != Routes.SIGN_IN) {
                navController.navigate(Routes.SIGN_IN) { popUpTo(0) }
            }
            AppStartState.NeedsOnboarding -> if (currentRoute != Routes.ONBOARDING) {
                navController.navigate(Routes.ONBOARDING) { popUpTo(0) }
            }
            AppStartState.Ready -> {
                val stillOnASubScreen = currentRoute == Routes.HOME ||
                    currentRoute == Routes.PROFILE ||
                    currentRoute == Routes.ROADMAP_OVERVIEW ||
                    currentRoute == Routes.PRACTICE_SCENARIO_PICKER ||
                    currentRoute.orEmpty().startsWith("lesson/") ||
                    currentRoute.orEmpty().startsWith("quiz/") ||
                    currentRoute.orEmpty().startsWith("practice/")
                if (!stillOnASubScreen) {
                    navController.navigate(Routes.HOME) { popUpTo(0) }
                }
            }
            AppStartState.Loading -> Unit
        }
    }

    if (startState == AppStartState.Loading) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
        return
    }

    NavHost(navController = navController, startDestination = Routes.SIGN_IN) {
        composable(Routes.SIGN_IN) { SignInScreen() }
        composable(Routes.ONBOARDING) { OnboardingScreen(onOnboardingComplete = rootViewModel::markOnboardingComplete) }
        composable(Routes.HOME) {
            HomeScreen(
                onLessonClick = { lessonId -> navController.navigate(Routes.lesson(lessonId)) },
                onProfileClick = { navController.navigate(Routes.PROFILE) },
                onQuizClick = { quizId -> navController.navigate(Routes.quiz(quizId)) },
                // Practice is always tied to today's topic — no free-pick menu, straight to the conversation.
                onPracticeClick = { topic -> navController.navigate(Routes.practiceConversation(topic)) },
                onRoadmapOverviewClick = { navController.navigate(Routes.ROADMAP_OVERVIEW) },
                onPracticeScenarioPickerClick = { navController.navigate(Routes.PRACTICE_SCENARIO_PICKER) },
            )
        }
        composable(Routes.ROADMAP_OVERVIEW) {
            RoadmapOverviewScreen(onBack = { navController.popBackStack() })
        }
        composable(Routes.PRACTICE_SCENARIO_PICKER) {
            PracticeScenarioPickerScreen(
                onBack = { navController.popBackStack() },
                onSituationChosen = { situation -> navController.navigate(Routes.practiceConversation(situation)) },
            )
        }
        composable(Routes.PROFILE) {
            ProfileScreen(onBack = { navController.popBackStack() })
        }
        composable(Routes.LESSON) { backStackEntry ->
            val lessonId = backStackEntry.arguments?.getString("lessonId") ?: return@composable
            LessonScreen(lessonId = lessonId, onLessonFinished = { navController.popBackStack() })
        }
        composable(Routes.QUIZ) { backStackEntry ->
            val quizId = backStackEntry.arguments?.getString("quizId") ?: return@composable
            QuizScreen(quizId = quizId, onFinished = { navController.popBackStack() })
        }
        composable(Routes.PRACTICE_CONVERSATION) { backStackEntry ->
            val topic = backStackEntry.arguments?.getString("topic") ?: return@composable
            PracticeConversationScreen(topic = topic, onBack = { navController.popBackStack() })
        }
    }
}
