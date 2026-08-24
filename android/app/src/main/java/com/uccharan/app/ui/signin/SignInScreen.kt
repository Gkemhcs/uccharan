package com.uccharan.app.ui.signin

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material.icons.outlined.Circle
import androidx.compose.material.icons.outlined.Email
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import com.uccharan.app.R
import com.uccharan.app.di.LocalAppContainer
import com.uccharan.app.di.uccharanViewModel
import com.uccharan.app.ui.theme.LocalUccharanGradients

// Phone sign-in (PhoneSignInScreen/PhoneSignInViewModel) is fully built and
// tested, but hidden from the UI: Firebase Phone Auth requires the paid
// Blaze plan (BILLING_NOT_ENABLED otherwise, no code-level workaround) and
// this project deliberately stays on the free Spark plan. Re-enabling is a
// two-line change — add the `showPhoneSignIn` state back and the "Continue
// with phone number" button below — once/if the project upgrades to Blaze.

@Composable
fun SignInScreen() {
    val context = LocalContext.current
    val container = LocalAppContainer.current
    val viewModel = uccharanViewModel { SignInViewModel(container.authRepository, container.userProfileRepository) }
    val uiState by viewModel.uiState.collectAsState()
    val gradients = LocalUccharanGradients.current
    var passwordVisible by remember { mutableStateOf(false) }

    Box(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        HeroBackdrop()

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 28.dp)
                .padding(top = 16.dp, bottom = 24.dp),
            verticalArrangement = Arrangement.Center,
        ) {
            val isSignUp = uiState.mode == AuthMode.CREATE_ACCOUNT

            BrandMark()
            Spacer(modifier = Modifier.height(30.dp))

            Text(
                text = if (isSignUp) "Let's get\nstarted." else "Speak with\nconfidence.",
                style = MaterialTheme.typography.displaySmall,
                color = MaterialTheme.colorScheme.onBackground,
            )
            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text = "Practice out loud. Get corrected, gently — in English, and in your own language too.",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(32.dp))

            if (isSignUp) {
                OutlinedTextField(
                    value = uiState.name,
                    onValueChange = viewModel::onNameChange,
                    label = { Text("Your name") },
                    leadingIcon = { Icon(Icons.Outlined.Person, contentDescription = null) },
                    shape = RoundedCornerShape(14.dp),
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    colors = uccharanTextFieldColors(),
                )
                Spacer(modifier = Modifier.height(12.dp))
            }
            OutlinedTextField(
                value = uiState.email,
                onValueChange = viewModel::onEmailChange,
                label = { Text("Email") },
                leadingIcon = { Icon(Icons.Outlined.Email, contentDescription = null) },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                shape = RoundedCornerShape(14.dp),
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
                colors = uccharanTextFieldColors(),
            )
            Spacer(modifier = Modifier.height(12.dp))
            OutlinedTextField(
                value = uiState.password,
                onValueChange = viewModel::onPasswordChange,
                label = { Text("Password") },
                leadingIcon = { Icon(Icons.Outlined.Lock, contentDescription = null) },
                trailingIcon = {
                    IconButton(onClick = { passwordVisible = !passwordVisible }) {
                        Icon(
                            if (passwordVisible) Icons.Filled.VisibilityOff else Icons.Filled.Visibility,
                            contentDescription = if (passwordVisible) "Hide password" else "Show password",
                        )
                    }
                },
                visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                shape = RoundedCornerShape(14.dp),
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
                colors = uccharanTextFieldColors(),
            )

            if (isSignUp && uiState.password.isNotEmpty()) {
                PasswordRequirementsChecklist(password = uiState.password)
            }

            uiState.errorMessage?.let { message ->
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 10.dp),
                )
            }
            // Never asserted as certain — see SignInViewModel's doc on why this
            // also shows up for an ambiguous "wrong password vs no account" error.
            if (uiState.suggestCreateAccount) {
                Text(
                    text = "New here? Create an account instead",
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.Bold,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 6.dp).clickableSingle(viewModel::switchToCreateAccount),
                )
            }

            Spacer(modifier = Modifier.height(22.dp))

            if (uiState.isLoading) {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
            } else if (isSignUp) {
                GradientButton(text = "Create account", brush = gradients.primaryButton, onClick = viewModel::signUp)
                Spacer(modifier = Modifier.height(20.dp))
                ModeSwitchLink(prompt = "Already have an account?", action = "Sign in", onClick = viewModel::switchToSignIn)
            } else {
                GradientButton(text = "Sign in", brush = gradients.primaryButton, onClick = viewModel::signIn)
                Spacer(modifier = Modifier.height(26.dp))
                DividerWithLabel(label = "OR CONTINUE WITH")
                Spacer(modifier = Modifier.height(20.dp))
                SecondaryOptionButton(
                    label = "Continue with Google",
                    leading = {
                        Text(
                            "G",
                            color = Color(0xFF4285F4),
                            fontWeight = FontWeight.ExtraBold,
                            style = MaterialTheme.typography.titleMedium,
                        )
                    },
                    onClick = { viewModel.signInWithGoogle(context) },
                )
                Spacer(modifier = Modifier.height(20.dp))
                ModeSwitchLink(prompt = "Don't have an account?", action = "Create one", onClick = viewModel::switchToCreateAccount)
            }
        }
    }
}

@Composable
private fun ModeSwitchLink(prompt: String, action: String, onClick: () -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth().clickableSingle(onClick),
        horizontalArrangement = Arrangement.Center,
    ) {
        Text(prompt, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.width(6.dp))
        Text(action, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
    }
}

@Composable
private fun HeroBackdrop() {
    Box(modifier = Modifier.fillMaxSize()) {
        Box(
            modifier = Modifier
                .size(340.dp)
                .offset(x = 140.dp, y = (-120).dp)
                .clip(CircleShape)
                .background(
                    Brush.radialGradient(
                        listOf(MaterialTheme.colorScheme.primary.copy(alpha = 0.16f), Color.Transparent),
                    ),
                ),
        )
        Box(
            modifier = Modifier
                .size(250.dp)
                .offset(x = (-130).dp, y = 60.dp)
                .clip(CircleShape)
                .background(
                    Brush.radialGradient(
                        listOf(MaterialTheme.colorScheme.tertiary.copy(alpha = 0.10f), Color.Transparent),
                    ),
                ),
        )
    }
}

@Composable
private fun BrandMark() {
    Row(verticalAlignment = Alignment.CenterVertically) {
        val gradients = LocalUccharanGradients.current
        Box(
            modifier = Modifier
                .size(44.dp)
                .shadow(elevation = 10.dp, shape = RoundedCornerShape(13.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
                .clip(RoundedCornerShape(13.dp))
                .background(gradients.primaryIcon),
            contentAlignment = Alignment.Center,
        ) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(2.5.dp)) {
                SoundBar(height = 8.dp, alpha = 0.55f)
                SoundBar(height = 16.dp, alpha = 1f)
                SoundBar(height = 20.dp, alpha = 0.85f)
                SoundBar(height = 11.dp, alpha = 0.55f)
            }
        }
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = stringResource(R.string.app_name),
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.primary,
        )
    }
}

@Composable
private fun SoundBar(height: androidx.compose.ui.unit.Dp, alpha: Float) {
    Box(
        modifier = Modifier
            .width(3.dp)
            .height(height)
            .clip(RoundedCornerShape(1.5.dp))
            .background(Color.White.copy(alpha = alpha)),
    )
}

@Composable
internal fun GradientButton(text: String, brush: Brush, onClick: () -> Unit, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .shadow(elevation = 16.dp, shape = RoundedCornerShape(16.dp), ambientColor = MaterialTheme.colorScheme.primary, spotColor = MaterialTheme.colorScheme.primary)
            .clip(RoundedCornerShape(16.dp))
            .background(brush)
            .clickableSingle(onClick)
            .padding(vertical = 17.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(text, style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onPrimary)
    }
}

@Composable
private fun SecondaryOptionButton(label: String, leading: @Composable () -> Unit, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(elevation = 3.dp, shape = RoundedCornerShape(16.dp))
            .clip(RoundedCornerShape(16.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickableSingle(onClick)
            .padding(vertical = 15.dp),
        contentAlignment = Alignment.Center,
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            leading()
            Text(label, style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onBackground)
        }
    }
}

@Composable
private fun DividerWithLabel(label: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        androidx.compose.material3.HorizontalDivider(modifier = Modifier.weight(1f), color = MaterialTheme.colorScheme.outline)
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(horizontal = 14.dp),
        )
        androidx.compose.material3.HorizontalDivider(modifier = Modifier.weight(1f), color = MaterialTheme.colorScheme.outline)
    }
}

@Composable
internal fun PasswordRequirementsChecklist(password: String) {
    Column(modifier = Modifier.padding(top = 10.dp, start = 4.dp)) {
        com.uccharan.app.data.validation.PASSWORD_REQUIREMENTS.forEach { requirement ->
            val met = requirement.isMet(password)
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 2.dp)) {
                Icon(
                    if (met) Icons.Filled.CheckCircle else Icons.Outlined.Circle,
                    contentDescription = null,
                    tint = if (met) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(14.dp),
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    requirement.label,
                    style = MaterialTheme.typography.bodySmall,
                    color = if (met) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
internal fun uccharanTextFieldColors() = OutlinedTextFieldDefaults.colors(
    focusedBorderColor = MaterialTheme.colorScheme.primary,
    unfocusedBorderColor = MaterialTheme.colorScheme.outline,
    focusedLabelColor = MaterialTheme.colorScheme.primary,
)

/** Thin naming wrapper so buttons built from Box+background read clearly as one clickable unit. */
internal fun Modifier.clickableSingle(onClick: () -> Unit): Modifier =
    this.then(Modifier.clickable(onClick = onClick))
