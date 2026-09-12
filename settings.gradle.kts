pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven {
            url = java.net.URI("https://maven.mozilla.org/maven2/")
        }
    }
}

rootProject.name = "YourBrowser"

include(":core:common")
include(":core:crypto")
include(":core:network")
include(":core:browser")
include(":feature:vault")
include(":feature:downloader")
include(":app")
