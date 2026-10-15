local({
  outcome <- tryCatch({
    result <- "correct"
    if (!exists("information_items", envir = globalenv()) || is.null(get("information_items", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !identical(sort(unique(tolower(trimws(as.character(information_items))))), c("b", "e", "f"))) {
      result <- "incorrect"
    }
    result
  }, error = function(e) "incorrect")
  cat(paste0("AL_OBSERVATION {\"outcome\":\"", outcome, "\"}\n"))
})
