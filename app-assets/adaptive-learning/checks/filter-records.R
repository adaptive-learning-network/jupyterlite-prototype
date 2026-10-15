local({
  outcome <- tryCatch({
    result <- "correct"
    if (!exists("n_mmr_dose1_x", envir = globalenv()) || is.null(get("n_mmr_dose1_x", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(as.numeric(n_mmr_dose1_x) == 46)) {
      result <- "incorrect"
    }
    result
  }, error = function(e) "incorrect")
  cat(paste0("AL_OBSERVATION {\"outcome\":\"", outcome, "\"}\n"))
})
