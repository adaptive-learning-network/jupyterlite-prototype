local({
  outcome <- tryCatch({
    result <- "correct"
    if (!exists("aggregate_tables", envir = globalenv()) || is.null(get("aggregate_tables", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !identical(sort(unique(tolower(trimws(as.character(aggregate_tables))))), c("b", "c", "e"))) {
      result <- "incorrect"
    }
    result
  }, error = function(e) "incorrect")
  cat(paste0("AL_OBSERVATION {\"outcome\":\"", outcome, "\"}\n"))
})
