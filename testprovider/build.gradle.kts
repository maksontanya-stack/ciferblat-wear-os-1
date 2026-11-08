plugins { id("com.android.application") }
android {
 namespace = "ru.meta.wearos.classic1.fixtures"
 compileSdk = 35
 defaultConfig { applicationId = "ru.meta.wearos.classic1.fixtures"; minSdk = 33; targetSdk = 33; versionCode = 1; versionName = "test-only" }
}
dependencies { implementation("androidx.wear.watchface:watchface-complications-data-source:1.2.1") }
