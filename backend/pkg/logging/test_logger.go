package logging

func ExampleLogger() {
	// FIRST STEP: Init logging config
	cfg := NewLoggingConfig(true, "DEBUG", "txt", 1)
	
	// SECOND STEP: Create base loggger and call 'BaseLogger' method 'InvokeLogging'
	bl := NewBaseLogger("0.0.1", "C:\\Users\\itursunov\\Documents\\GitlabProjects\\driverlog\\logs", cfg)
	bl.InvokeLogging()
	
	// [OPTIONAL] STEP: If you need uou can create subloggers
	logger := NewModuleLogger("HTTP_SERVER", "1.0", bl)
	_ = NewModuleLogger("HANDLER", "MAIN", logger)
	
	// [EXAMPLE] 
	logger.Debug("DEBUG MESSAGE") 		// print DEBUG_LEVEL message and call panic 
	logger.Info("INFO MESSAGE") 		// print INFO_LEVEL message and call panic 
	logger.Warn("WARN MESSAGE") 		// print WARN_LEVEL message and call panic 
	logger.Error("ERROR MESSAGE") 		// print ERROR_LEVEL message and call panic 
	logger.Critical("CRITICAL MESSAGE") // print ERROR_LEVEL message and call panic 
}