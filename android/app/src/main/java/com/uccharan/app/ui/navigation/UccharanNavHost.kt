package com.uccharan.app.ui.navigation

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
import com.uccharan.app.ui.signin.SignInScreen

private object Routes {
    const val SIGN_IN = "sign_in"
    const val ONBOARDING = "onboarding"
    const val HOME = "home"
    const val LESSON = "lesson/{lessonId}"
    fun lesson(lessonId: String) = "lesson/$lessonId"
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
            AppStartState.Ready -> if (currentRoute != Routes.HOME && !currentRoute.orEmpty().startsWith("lesson/")) {
                navController.navigate(Routes.HOME) { popUpTo(0) }
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
            HomeScreen(onLessonClick = { lessonId -> navController.navigate(Routes.lesson(lessonId)) })
        }
        composable(Routes.LESSON) { backStackEntry ->
            val lessonId = backStackEntry.arguments?.getString("lessonId") ?: return@composable
            LessonScreen(lessonId = lessonId, onLessonFinished = { navController.popBackStack() })
        }
    }
}
