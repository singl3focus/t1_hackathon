package config

import "github.com/ilyakaznacheev/cleanenv"

type Config struct {
	Server struct {
		Port string `yaml:"port"`
	} `yaml:"server"`

	Database struct {
		Host     string `yaml:"host"`
		Port     string `yaml:"port"`
		Username string `yaml:"user"`
		Password string `yaml:"password"`
		DBName   string `yaml:"dbname"`
		SSLMode  string `yaml:"sslmode"`
	} `yaml:"database"`

	Logger struct {
		LogsDirPath string `yaml:"logs_dir"`
		Enable      bool   `yaml:"enable"`
		Level       string `yaml:"level"`
		Format      string `yaml:"format"`
		SavingDays  int    `yaml:"saving_days"`
	} `yaml:"logger"`
}

func GetConfig() *Config {
	var cfg Config

	err := cleanenv.ReadConfig("./config.yaml", &cfg)
	if err != nil {
		panic(err)
	}

	return &cfg
}
