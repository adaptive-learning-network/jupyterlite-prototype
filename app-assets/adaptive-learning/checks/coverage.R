local({
  outcome <- tryCatch({
    result <- "correct"
    if (!exists("coverage_x", envir = globalenv()) || is.null(get("coverage_x", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(abs(as.numeric(coverage_x) - 0.92) < 1e-6)) {
      result <- "incorrect"
    }
    result
  }, error = function(e) "incorrect")
  cat(paste0("AL_OBSERVATION {\"outcome\":\"", outcome, "\"}\n"))
})
