local({
  outcome <- tryCatch({
    result <- "correct"
    if (!exists("n_records", envir = globalenv()) || is.null(get("n_records", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(as.numeric(n_records) == 139)) {
      result <- "incorrect"
    }
    if (!exists("first_date", envir = globalenv()) || is.null(get("first_date", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(substr(as.character(first_date), 1, 10) == "2025-01-06")) {
      result <- "incorrect"
    }
    if (!exists("last_date", envir = globalenv()) || is.null(get("last_date", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(substr(as.character(last_date), 1, 10) == "2025-06-23")) {
      result <- "incorrect"
    }
    if (!exists("n_locations", envir = globalenv()) || is.null(get("n_locations", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(as.numeric(n_locations) == 3)) {
      result <- "incorrect"
    }
    if (!exists("age_min", envir = globalenv()) || is.null(get("age_min", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(as.numeric(age_min) == 0)) {
      result <- "incorrect"
    }
    if (!exists("age_max", envir = globalenv()) || is.null(get("age_max", envir = globalenv()))) {
      result <- "incomplete"
    } else if (result == "correct" && !isTRUE(as.numeric(age_max) == 9)) {
      result <- "incorrect"
    }
    result
  }, error = function(e) "incorrect")
  cat(paste0("AL_OBSERVATION {\"outcome\":\"", outcome, "\"}\n"))
})
