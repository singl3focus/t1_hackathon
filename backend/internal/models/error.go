package models

type AppError struct {
	Code         int    // Код ошибки (например, 404, 500 и т.д.)
	Message      string // Сообщение для пользователя
	Err          error  // Подробная информация об ошибке (можно не показывать пользователю)
	IsUserFacing bool   // Может ли ошибка быть показана пользователю
}