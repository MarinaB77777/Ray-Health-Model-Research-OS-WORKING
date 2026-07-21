Measurement Setup — это посредник между инструментом измерения и первым кубиком.

Она делает не анализ, а:

1. Finds / selects measurement instrument
2. Reads or receives instrument metadata
3. Starts measurement process
4. Receives result of measurement
5. Forms Measurement Package for Cube 1

То есть для разных источников:

Questionnaire:
Measurement Setup → calls questionnaire start page/function
→ questionnaire completed
→ answers + questionnaire metadata
→ Measurement Package

Camera:
Measurement Setup → connects camera
→ start recording
→ stop recording
→ video file + camera metadata
→ Measurement Package

Sensor:
Measurement Setup → connects device
→ start capture
→ stop capture
→ raw file/stream export + device metadata
→ Measurement Package

Значит правильные кнопки на странице не “Build Measurement Graph”, а:

Connect / Select
Start Measurement
Finish Measurement
Create Measurement Package
Save Measurement

И да: первый кубик получает уже Measurement Package, а не сам напрямую дергает анкету/камеру/сенсор.