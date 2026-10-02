local({
  outcome <- tryCatch({
    result <- "correct"
    if (!exists("ill_exposed", envir = globalenv()) || is.null(get("ill_exposed", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(as.numeric(ill_exposed) == 30)) {
      result <- "incorrect"
    }
    result
  }, error = function(e) "incorrect")
  cat(paste0("AL_OBSERVATION {\"outcome\":\"", outcome, "\"}\n"))
})
