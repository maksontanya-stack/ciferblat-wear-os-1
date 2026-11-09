plugins { id("com.android.application") }
android {
    namespace = "ru.meta.wearos.classic1"
    compileSdk = 36
    defaultConfig {
        applicationId = "ru.meta.wearos.classic1"
        minSdk = 36
        targetSdk = 36
        versionCode = 6
        versionName = "1.2.0-preview.4"
    }
    buildTypes {
        debug {
            isMinifyEnabled = true
            isShrinkResources = false
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = false
        }
    }
}
