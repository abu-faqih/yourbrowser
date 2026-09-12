package com.yourbrowser.core.common.result

sealed class Resource<out T> {
    data class Success<out T>(val data: T) : Resource<T>()
    data class Error(val message: String, val cause: Throwable? = null) : Resource<Nothing>()
    data object Loading : Resource<Nothing>()

    inline fun <R> map(transform: (T) -> R): Resource<R> {
        return when (this) {
            is Success -> Success(transform(data))
            is Error -> Error(message, cause)
            is Loading -> Loading
        }
    }
}
