package com.uccharan.app.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Chat
import androidx.compose.material.icons.filled.Home
import androidx.compose.ui.graphics.vector.ImageVector

/**
 * The bottom-navigation tabs inside [MainShellScreen]. A plain enum on
 * purpose — adding a future tab (e.g. "Progress") is just one more entry
 * here plus one more `when` branch in the shell's content switch, nothing
 * structural to change.
 */
enum class MainTab(val label: String, val icon: ImageVector) {
    HOME("Home", Icons.Filled.Home),
    PRACTICE("Practice", Icons.AutoMirrored.Filled.Chat),
}
