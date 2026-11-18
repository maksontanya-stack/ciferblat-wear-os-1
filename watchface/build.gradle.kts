plugins { id("com.android.application") }
android {
    namespace = "ru.meta.wearos.classic11"
    compileSdk = 36
    defaultConfig {
        applicationId = "ru.meta.wearos.classic11"
        minSdk = 36
        targetSdk = 36
        versionCode = 6
        versionName = "1.1.5"
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
