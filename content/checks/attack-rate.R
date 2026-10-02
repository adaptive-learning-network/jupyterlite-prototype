local({
  outcome <- tryCatch({
    result <- "correct"
    if (!exists("ar_exposed", envir = globalenv()) || is.null(get("ar_exposed", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(abs(as.numeric(ar_exposed) - 0.75) < 1e-6)) {
      result <- "incorrect"
    }
    if (!exists("ar_unexposed", envir = globalenv()) || is.null(get("ar_unexposed", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(abs(as.numeric(ar_unexposed) - 0.25) < 1e-6)) {
      result <- "incorrect"
    }
    result
  }, error = function(e) "incorrect")
  cat(paste0("AL_OBSERVATION {\"outcome\":\"", outcome, "\"}\n"))
})
