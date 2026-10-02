local({
  outcome <- tryCatch({
    result <- "correct"
    if (!exists("answer", envir = globalenv()) || is.null(get("answer", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(tolower(trimws(as.character(answer))) == "b")) {
      result <- "incorrect"
    }
    result
  }, error = function(e) "incorrect")
  cat(paste0("AL_OBSERVATION {\"outcome\":\"", outcome, "\"}\n"))
})
