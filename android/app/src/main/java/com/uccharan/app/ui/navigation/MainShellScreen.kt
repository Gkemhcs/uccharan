package com.uccharan.app.ui.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import com.uccharan.app.ui.home.HomeScreen
import com.uccharan.app.ui.practice.PracticeTabScreen

/**
 * The app's main shell once signed in and onboarded: a persistent top bar
 * ("Uccharan" + profile) and a bottom tab bar, with each tab's content
 * swapped in below — not a nested NavHost, since these tabs don't need
 * independent back-stacks or deep links; a plain state switch is simpler
 * and has fewer ways to go wrong for just a couple of tabs. Adding a future
 * tab is one more [MainTab] entry plus one more branch below.
 *
 * Drill-down destinations (a lesson, a quiz, a practice conversation, the
 * full roadmap, Profile) are pushed on the OUTER NavHost on top of this
 * shell instead of living inside it — those are immersive, one-purpose
 * screens that shouldn't show the bottom tab bar while active.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainShellScreen(
    onLessonClick: (String) -> Unit,
    onQuizClick: (String) -> Unit,
    onRoadmapOverviewClick: () -> Unit,
    onProfileClick: () -> Unit,
    onPracticeSituationChosen: (String) -> Unit,
    onListeningPracticeClick: (String) -> Unit,
) {
    var selectedTab by rememberSaveable { mutableStateOf(MainTab.HOME) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Uccharan", fontWeight = FontWeight.Bold) },
                actions = {
                    IconButton(onClick = onProfileClick) {
                        Icon(Icons.Filled.AccountCircle, contentDescription = "Profile & settings")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.background),
            )
        },
        bottomBar = {
            NavigationBar {
                MainTab.entries.forEach { tab ->
                    NavigationBarItem(
                        selected = selectedTab == tab,
                        onClick = { selectedTab = tab },
                        icon = { Icon(tab.icon, contentDescription = tab.label) },
                        label = { Text(tab.label) },
                    )
                }
            }
        },
    ) { innerPadding ->
        Box(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
            when (selectedTab) {
                MainTab.HOME -> HomeScreen(
                    onLessonClick = onLessonClick,
                    onQuizClick = onQuizClick,
                    onRoadmapOverviewClick = onRoadmapOverviewClick,
                )
                MainTab.PRACTICE -> PracticeTabScreen(onSituationChosen = onPracticeSituationChosen, onListeningPracticeClick = onListeningPracticeClick)
            }
        }
    }
}
