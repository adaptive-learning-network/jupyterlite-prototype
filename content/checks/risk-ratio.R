local({
  outcome <- tryCatch({
    result <- "correct"
    if (!exists("risk_ratio", envir = globalenv()) || is.null(get("risk_ratio", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(abs(as.numeric(risk_ratio) - 3.0) < 1e-6)) {
      result <- "incorrect"
    }
    result
  }, error = function(e) "incorrect")
  cat(paste0("AL_OBSERVATION {\"outcome\":\"", outcome, "\"}\n"))
})
