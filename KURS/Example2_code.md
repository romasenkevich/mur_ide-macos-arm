ПРИЛОЖЕНИЕ Б
УЧРЕЖДЕНИЕ ОБРАЗОВАНИЯ
«БРЕСТСКИЙ ГОСУДАРСТВЕННЫЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ»
КАФЕДРА ИНТЕЛЛЕКТУАЛЬНЫХ ИНФОРМАЦИОННЫХ ТЕХНОЛОГИЙ

Разработка программы для автоматического движения АНПА по заданной траектории в симуляторе MUR IDE
Программный код основных модулей
КР.ИИ28.240141-01 12 00
Листов 11







Руководитель
А.А. Козинский
Выполнил
Я.М. Корнелюк










2026
СОДЕРЖАНИЕ
Class Config – модуль конфигурации, содержащий параметры движения и настройки.
Class Motion Controller – модуль управления движением, содержащий регуляторы, стабилизацию, повороты.
Class TelemetryLogger – модуль телеметрии и логирования, осуществляющий вывод в консоль и запись в файл.
Class TrajectoryGenerator – модуль формирования траекторий, который генерирует и выполняет траекторию движения.
Class UserInterface – модуль интерфейса пользователя.



























Config
class Config:
    # Параметры движения
    BASE_SPEED = 50
    DEPTH_TARGET = 1.2
    TURN_SPEED = 55
    
    # Параметры времени
    TURN_TIMEOUT = 12.0
    STABILIZATION_TIME = 3.5
    FINE_STABILIZATION_TIME = 2.5
    STABLE_CHECK_DURATION = 1.2
    
    # Параметры траекторий
    CIRCLE_RADIUS = 2.0
    SQUARE_SIDE = 3.0
    TRIANGLE_SIDE = 3.0
    CYCLES = 1
    
    # Папка для логов
    LOG_DIR = "trajectory_logs"

MotionController
class MotionController:
    
    def __init__(self, auv):
        self.auv = auv
        self.movement_start_time = None
        self.traj_type = 'unknown'
        self.traj_params = ''
        
        # Переменные для телеметрии
        self.last_telemetry_time = 0
        self.telemetry_interval = 0.5
        self.last_status_time = 0
        self.status_interval = 5.0
    
    # Вспомогательные функции для углов
    def clamp(self, v, min_val, max_val):
        if v < min_val:
            return min_val
        if v > max_val:
            return max_val
        return v
    
    def clamp_to_360(self, angle):
        while angle < 0.0:
            angle += 360.0
        while angle >= 360.0:
            angle -= 360.0
        return angle
    
    def to_180(self, angle):
        angle = self.clamp_to_360(angle)
        if angle > 180.0:
            return angle - 360.0
        return angle
    
    def normalize_angle(self, angle):
        return self.to_180(angle)
    
    def angle_diff(self, target, current):
        diff = target - current
        diff = self.to_180(diff)
        return diff
    
    def add_angle(self, angle, delta):
        return self.normalize_angle(angle + delta)
    
    # Функции управления
    # П-регулятор курса
    def keep_yaw(self, target_heading, power):
        current_yaw = self.auv.get_yaw()
        error = self.angle_diff(target_heading, current_yaw)
        
        kp = 0.8
        correction = error * -kp
        
        left_speed = self.clamp(int(power - correction), -100, 100)
        right_speed = self.clamp(int(power + correction), -100, 100)
        
        self.auv.set_motor_power(0, left_speed)
        self.auv.set_motor_power(1, right_speed)
    
    # П-регулятор глубины
    def keep_depth(self, target_depth):
        error = self.auv.get_depth() - target_depth
        kp = 80
        power = int(kp * error)
        power = self.clamp(power, -100, 100)
        
        self.auv.set_motor_power(2, power)
        self.auv.set_motor_power(3, power)
    
    # Полная остановка всех двигателей
    def stop_motors(self):
        self.auv.set_motor_power(0, 0)
        self.auv.set_motor_power(1, 0)
        self.auv.set_motor_power(2, 0)
        self.auv.set_motor_power(3, 0)
    
    def get_mission_time(self):
        if self.movement_start_time is None:
            return 0
        return time.time() - self.movement_start_time
    
    # Проверка стабильности курса
    def is_heading_stable(self, target_heading, precision=2.0, duration=None):
        if duration is None:
            duration = Config.STABLE_CHECK_DURATION
        start_time = time.time()
        stable_count = 0
        
        while time.time() - start_time < duration:
            current_heading = self.auv.get_yaw()
            error = abs(self.angle_diff(target_heading, current_heading))
            
            if error <= precision:
                stable_count += 1
            else:
                stable_count = 0
            
            if stable_count > duration * 20:
                return True
            
            time.sleep(0.05)
        
        return stable_count > 5
    
    # Стабилизаци курса с проверкой точности
    def stabilize_heading(self, target_heading, target_depth, precision=2.5, max_duration=None):
        if max_duration is None:
            max_duration = Config.STABILIZATION_TIME
        print(f"\n      Стабилизация курса {target_heading:.1f}°...")
        start_time = time.time()
        
        while time.time() - start_time < max_duration:
            current_heading = self.auv.get_yaw()
            error = self.angle_diff(target_heading, current_heading)
            
            self.print_telemetry(status_message="стабилизация")
            
            if abs(error) <= precision:
                if self.is_heading_stable(target_heading, precision, 1.0):
                    print(f"\n      Курс стабилизирован: {current_heading:.1f}°")
                    self.stop_motors()
                    time.sleep(0.3)
                    return True
            
            self.keep_yaw(target_heading, 0)
            self.keep_depth(target_depth)
            time.sleep(0.05)
        
        final_heading = self.auv.get_yaw()
        final_error = self.angle_diff(target_heading, final_heading)
        print(f"\n      Стабилизация завершена, ошибка: {final_error:.1f}°")
        
        self.stop_motors()
        time.sleep(0.3)
        return abs(final_error) <= precision * 2
    
    # Движение вперед с удержанием курса и глубины
    def move_forward(self, duration, target_heading, target_depth):
        stabilized = self.stabilize_heading(target_heading, target_depth, 3.0, Config.STABILIZATION_TIME)
        
        if not stabilized:
            print(f"      Предупреждение: курс не стабилизирован ({self.auv.get_yaw():.1f}° вместо {target_heading:.1f}°)")
            print(f"      Повторная стабилизация...")
            self.stabilize_heading(target_heading, target_depth, 5.0, Config.STABILIZATION_TIME)
        
        current_heading = self.auv.get_yaw()
        heading_error = abs(self.angle_diff(target_heading, current_heading))
        if heading_error > 5.0:
            print(f"      ВНИМАНИЕ! Начинаем движение с ошибкой курса {heading_error:.1f}°")
        else:
            print(f"      Курс проверен: {current_heading:.1f}° (ошибка: {heading_error:.1f}°)")
        
        print(f"      Движение вперед {duration:.1f} сек...")
        start_time = time.time()
        last_log_time = start_time
        
        while time.time() - start_time < duration:
            self.keep_yaw(target_heading, Config.BASE_SPEED)
            self.keep_depth(target_depth)
            
            self.print_telemetry(status_message="движение")
            
            if time.time() - last_log_time >= 0.5:
                self.log_data(target_heading)
                last_log_time = time.time()
            
            time.sleep(0.05)
        
        self.stop_motors()
        print()
        time.sleep(0.5)
    
    # Поворот с последующей точной стабилизацией курса
    def turn_with_stabilization(self, angle, target_depth):
        current_heading = self.auv.get_yaw()
        target_heading = self.add_angle(current_heading, angle)
        
        print(f"\n      Поворот: {current_heading:.1f}° -> {target_heading:.1f}°")
        
        self.stop_motors()
        time.sleep(0.5)
        
        turn_start_time = time.time()
        turn_timeout = Config.TURN_TIMEOUT
        direction = 1 if angle > 0 else -1
        last_log_time = turn_start_time
        
        while time.time() - turn_start_time < turn_timeout:
            current_heading = self.auv.get_yaw()
            error = self.angle_diff(target_heading, current_heading)
            
            self.print_telemetry(status_message=f"поворот, осталось {abs(error):.1f}°")
            
            if time.time() - last_log_time >= 0.5:
                self.log_data(target_heading)
                last_log_time = time.time()
            
            if abs(error) < 5.0:
                print(f"\n      Достигнут целевой угол: {current_heading:.1f}°")
                break
            
            if direction == 1 and error < 0:
                print(f"\n      Перешли цель: текущий {current_heading:.1f}°")
                break
            
            if direction == -1 and error > 0:
                print(f"\n      Перешли цель: текущий {current_heading:.1f}°")
                break
            
            speed = Config.TURN_SPEED * direction
            self.auv.set_motor_power(0, -speed)
            self.auv.set_motor_power(1, speed)
            self.keep_depth(target_depth)
            
            time.sleep(0.05)
        else:
            print(f"\n      Таймаут поворота, текущий курс: {self.auv.get_yaw():.1f}°")
        
        self.stop_motors()
        print()
        time.sleep(0.5)
        
        print(f"      Точная стабилизация курса...")
        
        self.stabilize_heading(target_heading, target_depth, 5.0, Config.STABILIZATION_TIME)
        self.stabilize_heading(target_heading, target_depth, 3.0, Config.STABILIZATION_TIME)
        self.stabilize_heading(target_heading, target_depth, 2.0, Config.FINE_STABILIZATION_TIME)
        
        final_heading = self.auv.get_yaw()
        final_error = self.angle_diff(target_heading, final_heading)
        
        retry_count = 0
        while abs(final_error) > 5.0 and retry_count < 3:
            print(f"      Ошибка {final_error:.1f}° > 5°, повторная стабилизация (попытка {retry_count + 1}/3)...")
            self.stabilize_heading(target_heading, target_depth, 2.0, Config.FINE_STABILIZATION_TIME)
            final_heading = self.auv.get_yaw()
            final_error = self.angle_diff(target_heading, final_heading)
            retry_count += 1
        
        if abs(final_error) <= 1.5:
            print(f"      ОТЛИЧНО! Ошибка: {final_error:.1f}°")
            success = True
        elif abs(final_error) <= 3.0:
            print(f"      ХОРОШО! Ошибка: {final_error:.1f}°")
            success = True
        elif abs(final_error) <= 5.0:
            print(f"      ПРИЕМЛЕМО. Ошибка: {final_error:.1f}°")
            success = True
        else:
            print(f"      ВНИМАНИЕ! Ошибка: {final_error:.1f}°")
            success = False
        
        return success
    
    # Установка информации о траектории для логирования
    def set_trajectory_info(self, traj_type, traj_params):
        self.traj_type = traj_type
        self.traj_params = traj_params
    
    # Начало отсчета времени миссии
    def start_mission_time(self):
        if self.movement_start_time is None:
            self.movement_start_time = time.time()
            print(f"      Начало отсчета времени миссии")
    
    # Сброс времени миссии
    def reset_mission_time(self):
        self.movement_start_time = None



TelemetryLogger
class TelemetryLogger:

    def __init__(self, motion_controller):
        self.mc = motion_controller
        self.log_filename = None
        self.log_file = None
        self.log_writer = None
    
    # Создание папки для логов если её нет
    def ensure_log_dir(self):
        if not os.path.exists(Config.LOG_DIR):
            os.makedirs(Config.LOG_DIR)
            print(f"  Создана папка для логов: {Config.LOG_DIR}")
    
    # Инициализация логирования с расширенными полями
    def init_logging(self):
        self.ensure_log_dir()
        
        self.log_filename = f"trajectory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        log_path = os.path.join(Config.LOG_DIR, self.log_filename)
        self.log_file = open(log_path, 'w', newline='', encoding='utf-8')
        self.log_writer = csv.writer(self.log_file, delimiter=';')
        
        # Расширенные заголовки для анализа
        self.log_writer.writerow([
            'timestamp',           # Абсолютное время
            'time_elapsed',        # Время от начала движения (сек)
            'heading',             # Текущий курс (градусы)
            'target_heading',      # Целевой курс (градусы)
            'depth',               # Текущая глубина (м)
            'target_depth',        # Целевая глубина (м)
            'speed_ms',            # Скорость (м/с)
            'trajectory_type',     # Тип траектории
            'trajectory_params'    # Параметры траектории
        ])
        
        print(f"  Лог будет сохранен в: {Config.LOG_DIR}/{self.log_filename}")
    
    # Запись текущих данных в CSV
    def log_data(self, target_heading=0):
        if self.log_writer is None:
            return
            
        try:
            elapsed = self.mc.get_mission_time()
            current_heading = self.mc.auv.get_yaw()
            current_depth = self.mc.auv.get_depth()
            
            # Расчет скорости (м/с)
            speed_ms = Config.BASE_SPEED / 100.0 * 0.6
            
            self.log_writer.writerow([
                f"{time.time():.3f}",           # timestamp
                f"{elapsed:.3f}",                # time_elapsed
                f"{current_heading:.3f}",        # heading
                f"{target_heading:.3f}",         # target_heading
                f"{current_depth:.3f}",          # depth
                f"{Config.DEPTH_TARGET:.3f}",    # target_depth
                f"{speed_ms:.3f}",               # speed_ms
                f"{self.mc.traj_type}",          # trajectory_type
                f"{self.mc.traj_params}"         # trajectory_params
            ])
            self.log_file.flush()
        except Exception as e:
            pass
    
    # Закрытие файла логирования
    def close_logging(self):
        if self.log_file:
            self.log_file.close()
            print(f"  Лог сохранен в папку: {Config.LOG_DIR}")
    
    # Вывод текущих параметров движения в консоль
    def print_telemetry(self, status_message=""):
        current_time = time.time()
        
        # Вывод статуса каждые 5 секунд
        if status_message and (current_time - self.mc.last_status_time >= self.mc.status_interval):
            print(f"\n[STATUS] {status_message}")
            self.mc.last_status_time = current_time
        
        # Вывод телеметрии с заданным интервалом
        if current_time - self.mc.last_telemetry_time < self.mc.telemetry_interval:
            return
        
        self.mc.last_telemetry_time = current_time
        
        try:
            current_heading = self.mc.auv.get_yaw()
            current_depth = self.mc.auv.get_depth()
            speed = Config.BASE_SPEED / 100.0 * 0.6
            mission_time = self.mc.get_mission_time()
            time_str = f"{mission_time:.1f} сек"
            
            print(f"\r  Курс:{current_heading:6.1f}° | Глубина:{current_depth:4.2f}м | Скорость:{speed:3.2f}м/с | Время:{time_str:>10} | {status_message}", end="", flush=True)
            
        except Exception as e:
            pass

# класс формирования траекторий (генерация и выполнения траекторий движения)
class TrajectoryGenerator:
    
    def __init__(self, motion_controller, logger):
        self.mc = motion_controller
        self.logger = logger
    
    # Ввод параметров для круга
    def get_circle_params(self):
        print("\n--- Параметры для траектории КРУГ ---")
        try:
            radius_input = input(f"Введите радиус круга в метрах [2.0]: ")
            if radius_input.strip():
                Config.CIRCLE_RADIUS = float(radius_input)
                if Config.CIRCLE_RADIUS < 0.5:
                    Config.CIRCLE_RADIUS = 0.5
                    print(f"    Радиус не может быть меньше 0.5 м, установлено: {Config.CIRCLE_RADIUS} м")
        except ValueError:
            Config.CIRCLE_RADIUS = 2.0
            print(f"    Использовано значение по умолчанию: {Config.CIRCLE_RADIUS} м")
        
        print(f"    Радиус круга: {Config.CIRCLE_RADIUS} м")
        self.mc.set_trajectory_info('circle', f'radius={Config.CIRCLE_RADIUS}')
        
        try:
            cycles_input = input(f"Введите количество циклов (повторений) [1]: ")
            if cycles_input.strip():
                Config.CYCLES = int(cycles_input)
                if Config.CYCLES < 1:
                    Config.CYCLES = 1
        except ValueError:
            Config.CYCLES = 1
        
        print(f"    Количество циклов: {Config.CYCLES}")
    
    #Ввод параметров для квадрата
    def get_square_params(self):
        print("\n--- Параметры для траектории КВАДРАТ ---")
        try:
            side_input = input(f"Введите длину стороны квадрата в метрах [3.0]: ")
            if side_input.strip():
                Config.SQUARE_SIDE = float(side_input)
                if Config.SQUARE_SIDE < 1.0:
                    Config.SQUARE_SIDE = 1.0
                    print(f"    Сторона не может быть меньше 1.0 м, установлено: {Config.SQUARE_SIDE} м")
        except ValueError:
            Config.SQUARE_SIDE = 3.0
            print(f"    Использовано значение по умолчанию: {Config.SQUARE_SIDE} м")
        
        print(f"    Сторона квадрата: {Config.SQUARE_SIDE} м")
        self.mc.set_trajectory_info('square', f'side={Config.SQUARE_SIDE}')
        
        try:
            cycles_input = input(f"Введите количество циклов (повторений) [1]: ")
            if cycles_input.strip():
                Config.CYCLES = int(cycles_input)
                if Config.CYCLES < 1:
                    Config.CYCLES = 1
        except ValueError:
            Config.CYCLES = 1
        
        print(f"    Количество циклов: {Config.CYCLES}")
    
    # Ввод параметров для треугольника
    def get_triangle_params(self):
        print("\n--- Параметры для траектории ТРЕУГОЛЬНИК ---")
        try:
            side_input = input(f"Введите длину стороны треугольника в метрах [3.0]: ")
            if side_input.strip():
                Config.TRIANGLE_SIDE = float(side_input)
                if Config.TRIANGLE_SIDE < 1.0:
                    Config.TRIANGLE_SIDE = 1.0
                    print(f"    Сторона не может быть меньше 1.0 м, установлено: {Config.TRIANGLE_SIDE} м")
        except ValueError:
            Config.TRIANGLE_SIDE = 3.0
            print(f"    Использовано значение по умолчанию: {Config.TRIANGLE_SIDE} м")
        
        print(f"    Сторона треугольника: {Config.TRIANGLE_SIDE} м")
        self.mc.set_trajectory_info('triangle', f'side={Config.TRIANGLE_SIDE}')
        
        try:
            cycles_input = input(f"Введите количество циклов (повторений) [1]: ")
            if cycles_input.strip():
                Config.CYCLES = int(cycles_input)
                if Config.CYCLES < 1:
                    Config.CYCLES = 1
        except ValueError:
            Config.CYCLES = 1
        
        print(f"    Количество циклов: {Config.CYCLES}")
    
    # Движение по окружности
    def trajectory_circle(self, radius, target_depth, cycles=1):
        for cycle in range(cycles):
            print(f"\n  Круг: цикл {cycle + 1}/{cycles}")
            
            circumference = 2 * math.pi * radius
            speed_ms = Config.BASE_SPEED / 100.0 * 0.6
            circle_time = circumference / speed_ms
            angular_speed = 360 / circle_time
            
            print(f"    Радиус: {radius} м, длина окружности: {circumference:.2f} м")
            print(f"    Время оборота: {circle_time:.1f} сек")
            
            start_heading = self.mc.auv.get_yaw()
            start_time = time.time()
            last_log_time = start_time
            
            self.mc.start_mission_time()
            
            while time.time() - start_time < circle_time:
                elapsed = time.time() - start_time
                target_heading = self.mc.add_angle(start_heading, angular_speed * elapsed)
                self.mc.keep_yaw(target_heading, Config.BASE_SPEED)
                self.mc.keep_depth(target_depth)
                
                self.logger.print_telemetry(status_message="круг")
                
                if time.time() - last_log_time >= 0.5:
                    self.logger.log_data(target_heading)
                    last_log_time = time.time()
                
                time.sleep(0.05)
            
            self.mc.stop_motors()
            print()
            time.sleep(1)
            print(f"      Цикл {cycle + 1} завершен")
    
    # Движение по квадрату
    def trajectory_square(self, side, target_depth, cycles=1):
        speed_ms = Config.BASE_SPEED / 100.0 * 0.6
        move_time = side / speed_ms
        
        for cycle in range(cycles):
            print(f"\n  Квадрат: цикл {cycle + 1}/{cycles}")
            print(f"    Сторона: {side} м, время движения: {move_time:.1f} сек")
            
            for side_num in range(4):
                print(f"\n    Сторона {side_num + 1}/4")
                
                current_heading = self.mc.auv.get_yaw()
                print(f"    Текущий курс: {current_heading:.1f}°")
                
                if side_num == 0 and cycle == 0:
                    self.mc.start_mission_time()
                
                self.mc.move_forward(move_time, current_heading, target_depth)
                
                if side_num < 3:
                    self.mc.turn_with_stabilization(90, target_depth)
                    after_turn_heading = self.mc.auv.get_yaw()
                    print(f"    Курс после поворота: {after_turn_heading:.1f}°")
            
            print(f"\n      Цикл {cycle + 1} завершен")
    
    # Движение по треугольнику
    def trajectory_triangle(self, side, target_depth, cycles=1):
        speed_ms = Config.BASE_SPEED / 100.0 * 0.6
        move_time = side / speed_ms
        
        for cycle in range(cycles):
            print(f"\n  Треугольник: цикл {cycle + 1}/{cycles}")
            print(f"    Сторона: {side} м, время движения: {move_time:.1f} сек")
            
            for side_num in range(3):
                print(f"\n    Сторона {side_num + 1}/3")
                
                current_heading = self.mc.auv.get_yaw()
                print(f"    Текущий курс: {current_heading:.1f}°")
                
                if side_num == 0 and cycle == 0:
                    self.mc.start_mission_time()
                
                self.mc.move_forward(move_time, current_heading, target_depth)
                
                if side_num < 2:
                    self.mc.turn_with_stabilization(120, target_depth)
                    after_turn_heading = self.mc.auv.get_yaw()
                    print(f"    Курс после поворота: {after_turn_heading:.1f}°")
            
            print(f"\n      Цикл {cycle + 1} завершен")

UserInterface
class UserInterface:
    
    def __init__(self):
        self.mc = MotionController(auv)
        self.logger = TelemetryLogger(self.mc)
        self.trajectory = TrajectoryGenerator(self.mc, self.logger)
        
        # Связываем методы логирования с контроллером
        self.mc.print_telemetry = self.logger.print_telemetry
        self.mc.log_data = self.logger.log_data
    
    def show_instructions(self):
        """Показать подробную инструкцию по использованию программы"""
        print("\n" + "=" * 70)
        print("  ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ ПРОГРАММЫ")
        print("=" * 70)
        
        print("\n  1. ОСНОВНЫЕ ВОЗМОЖНОСТИ:")
        print("     ┌─────────────────────────────────────────────────────────")
        print("     │ • Движение АНПА по трем типам траекторий:")
        print("     │   - Круг (с заданным радиусом)")
        print("     │   - Квадрат (с заданной длиной стороны)")
        print("     │   - Треугольник (с заданной длиной стороны)")
        print("     │ • Автоматическое удержание глубины (П-регулятор)")
        print("     │ • Стабилизация курса (П-регулятор)")
        print("     │ • Логирование данных в CSV файл")
        print("     └─────────────────────────────────────────────────────────")
        
        print("\n  2. ПОРЯДОК РАБОТЫ:")
        print("     ┌─────────────────────────────────────────────────────────")
        print("     │ ШАГ 1: Запустите программу")
        print("     │ ШАГ 2: Выберите пункт 1 'Выполнить миссию'")
        print("     │ ШАГ 3: Выберите тип траектории (1-Круг, 2-Квадрат, 3-Треугольник)")
        print("     │ ШАГ 4: Введите параметры траектории (размеры, количество циклов)")
        print("     │ ШАГ 5: Аппарат выполнит:")
        print("     │        - Погружение на заданную глубину")
        print("     │        - Стабилизацию курса")
        print("     │        - Движение по выбранной траектории")
        print("     │        - Автоматическое логирование данных")
        print("     │ ШАГ 6: После завершения данные сохранятся в папку 'trajectory_logs'")
        print("     └─────────────────────────────────────────────────────────")
        
        print("\n  3. НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ (в классе Config):")
        print("     ┌─────────────────────────────────────────────────────────")
        print("     │ • BASE_SPEED = 50        - базовая скорость движения")
        print("     │ • DEPTH_TARGET = 1.2     - целевая глубина (метры)")
        print("     │ • TURN_SPEED = 55        - скорость поворота")
        print("     │ • STABILIZATION_TIME = 3.5 - время стабилизации курса")
        print("     │ • CIRCLE_RADIUS = 2.0    - радиус круга (метры)")
        print("     │ • SQUARE_SIDE = 3.0      - сторона квадрата (метры)")
        print("     │ • TRIANGLE_SIDE = 3.0    - сторона треугольника (метры)")
        print("     └─────────────────────────────────────────────────────────")
        
        print("\n  4. ФОРМАТ ЛОГ-ФАЙЛА (CSV):")
        print("     ┌─────────────────────────────────────────────────────────")
        print("     │ • timestamp         - абсолютное время (сек)")
        print("     │ • time_elapsed      - время от начала движения (сек)")
        print("     │ • heading           - текущий курс (°)")
        print("     │ • target_heading    - целевой курс (°)")
        print("     │ • depth             - текущая глубина (м)")
        print("     │ • target_depth      - целевая глубина (м)")
        print("     │ • speed_ms          - скорость (м/с)")
        print("     │ • trajectory_type   - тип траектории")
        print("     │ • trajectory_params - параметры траектории")
        print("     └─────────────────────────────────────────────────────────")
        
        print("\n  5. ПРИМЕР ЗАПУСКА:")
        print("     ┌─────────────────────────────────────────────────────────")
        print("     │ python mur_trajectory.py      - интерактивный режим")
        print("     │ python mur_trajectory.py 1    - сразу запустить круг")
        print("     │ python mur_trajectory.py 2    - сразу запустить квадрат")
        print("     │ python mur_trajectory.py 3    - сразу запустить треугольник")
        print("     └─────────────────────────────────────────────────────────")
        
        print("\n  6. ПРИМЕЧАНИЯ:")
        print("     ┌─────────────────────────────────────────────────────────")
        print("     │ • Перед запуском убедитесь, что АНПА подключен")
        print("     │ • При остановке программы все двигатели отключаются")
        print("     │ • Лог-файлы создаются автоматически с меткой времени")
        print("     │ • Папка 'trajectory_logs' создается автоматически")
        print("     └─────────────────────────────────────────────────────────")
        
        print("\n" + "=" * 70)
        input("Нажмите Enter для возврата в главное меню...")
    
    def run_mission(self):
        """Выполнение одной миссии"""
        print("\n" + "=" * 60)
        print("Выберите траекторию:")
        print("   1 - Круг")
        print("   2 - Квадрат")
        print("   3 - Треугольник")
        print("=" * 60)
        
        if len(sys.argv) > 1:
            choice = sys.argv[1]
        else:
            choice = input("Введите номер траектории (1/2/3): ")
        
        # Запрос параметров
        if choice == '1':
            self.trajectory.get_circle_params()
        elif choice == '2':
            self.trajectory.get_square_params()
        elif choice == '3':
            self.trajectory.get_triangle_params()
        else:
            print("  Неверный выбор!")
            return False
        
        # Инициализация логирования
        self.logger.init_logging()
        
        print(f"\n  Настройки:")
        print(f"   Время стабилизации: {Config.STABILIZATION_TIME} сек")
        print(f"   Таймаут поворота: {Config.TURN_TIMEOUT} сек")
        print("=" * 60)
        
        # Погружение
        print(f"\n Погружение на глубину {Config.DEPTH_TARGET} м...")
        dive_start_time = time.time()
        while time.time() - dive_start_time < 5:
            self.mc.keep_depth(Config.DEPTH_TARGET)
            time.sleep(0.05)
        
        print("\n  Начальная глубина достигнута")
        self.mc.stop_motors()
        time.sleep(1)
        
        # Стабилизация курса
        initial_heading = self.mc.auv.get_yaw()
        print(f"\n  Текущий курс: {initial_heading:.1f}°")
        self.mc.stabilize_heading(initial_heading, Config.DEPTH_TARGET, 3.0, Config.STABILIZATION_TIME)
        
        print("\n  Начало движения...")
        print("=" * 60)
        
        # Сброс времени начала движения
        self.mc.reset_mission_time()
        
        # Выполнение траектории
        if choice == '1':
            self.trajectory.trajectory_circle(Config.CIRCLE_RADIUS, Config.DEPTH_TARGET, Config.CYCLES)
        elif choice == '2':
            self.trajectory.trajectory_square(Config.SQUARE_SIDE, Config.DEPTH_TARGET, Config.CYCLES)
        elif choice == '3':
            self.trajectory.trajectory_triangle(Config.TRIANGLE_SIDE, Config.DEPTH_TARGET, Config.CYCLES)
        
        # Завершение
        print("\n" + "=" * 60)
        print("  Остановка аппарата...")
        self.mc.stop_motors()
        
        total_time = self.mc.get_mission_time()
        print("\n  Миссия завершена!")
        print(f"  Данные сохранены в папку: {Config.LOG_DIR}")
        print(f"  Время движения: {total_time:.1f} сек")
        print("=" * 60)
        
        self.logger.close_logging()
        return True
    
    def main(self):
        print("=" * 60)
        print("  Управление АНПА с использованием П-регуляторов")
        print("   MUR IDE - движение по траекториям")
        print("=" * 60)
        
        while True:
            print("\n" + "=" * 60)
            print("ГЛАВНОЕ МЕНЮ:")
            print("   1 - Выполнить миссию (круг, квадрат, треугольник)")
            print("   2 - Показать инструкцию")
            print("   3 - Выход из программы")
            print("=" * 60)
            
            action = input("Введите номер (1/2/3): ")
            
            if action == '1':
                self.run_mission()
            elif action == '2':
                self.show_instructions()
            elif action == '3':
                print("\nПрограмма завершена.")
                break
            else:
                print("  Неверный выбор! Попробуйте снова.")
            
            print("\n" + "-" * 60)
            input("Нажмите Enter для возврата в главное меню...")
