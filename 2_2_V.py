from manim import *
import numpy as np
import json


class dater(ZoomedScene):

    # задаем конфигурацию окна зума
    def __init__(self, **kwargs):
        ZoomedScene.__init__(
            self,
            zoom_factor=0.2,
            zoomed_display_height=7,
            zoomed_display_width=5,
            image_frame_stroke_width=0.15,
            zoomed_camera_config={
                "default_frame_stroke_width": 0.1,
            },
            **kwargs
        )

    def construct(self):

        # число векторов. задавать только четным.
        quantity = 10

        # замедление анимации
        zamedlenie = 0.05

        # длина основной анимации
        len_of_main_animation = 13
        portrait_zoom = 0.0051

        # файл со сглаженной прямой
        fp = open('portrait.json', 'r')

        # смещение рисунка в лево
        sdvig = -3

        # рисовать ли доп анимации появления векторов и зума (см. # 6. и # 7.). 0 - нет, 1 - да
        choice = 1

        # рисовать ли портрет (см. # 5.)
        choice_1 = 1

        # рисовать ли стрелки
        choice_3 = 1

        ######################################################################################################################################
        # 1. Расчет длин векторов
        ######################################################################################################################################

        # используется в расчете длин векторов (см. # 1.) и при отрисовки контура портрета (см. # 6.)
        data = np.array(json.load(fp))
        fp.close()

        res = data[:, 0]
        ims = -data[:, 1]

        cmplxs = res + 1j * ims
        phis = np.linspace(0, 2 * np.pi, len(data) + 1)[:-1]

        def cn(n):
            exparr = np.exp(-1j * n * phis)
            return (np.sum(exparr * cmplxs)) / len(data)

        cns = np.array([cn(i) for i in range(-quantity // 2, quantity // 2 + 1)])

        # разворачиваю список координат стрелок в нужном порядке - 0, 1, -1, 2, -2 ...
        cms = [0]
        for i in range(len(cns) // 2):
            cms.append(cns[quantity // 2 + 1 + i])
            cms.append(cns[quantity // 2 - 1 - i])
        cms = np.array(cms)

        # уменьшаю картинку до размера экрана
        list_c = cms * portrait_zoom

        ######################################################################################################################################
        # 2. Создаю список векторов
        ######################################################################################################################################

        # список векторов
        Arrow_list = [
            Arrow([0, 0, 0],
                  [sdvig, 0, 0],
                  buff=0,
                  color=WHITE,
                  max_stroke_width_to_length_ratio=1.5,
                  max_tip_length_to_length_ratio=0.15)
        ]

        ll = sdvig
        for i_arrow in range(quantity):
            # координаты конца i_arrow вектора
            ll += list_c[i_arrow + 1]

            # тут [i_arrow - 1] потому что вектор должен начинаться на конце предыдущего
            Arrow_list.append(Arrow(Arrow_list[i_arrow - 1 + 1].get_end(),
                                    [ll.real, ll.imag, 0],
                                    buff=0,
                                    color=WHITE,
                                    max_stroke_width_to_length_ratio=1.5,
                                    max_tip_length_to_length_ratio=0.15))

        ######################################################################################################################################
        # 3. Цикл создающий список скоростей
        ######################################################################################################################################

        # список скоростей вращения векторов
        list_rot_speed = []
        b = 1
        # цикл создающий список скоростей
        for i in range(quantity):
            list_rot_speed.append(b * (i + 1))
            b *= -1

        ######################################################################################################################################
        # 4. Код создающий список функций вращения векторов
        ######################################################################################################################################
        list_func = []

        # i_func - номер вектора, в списке векторов. rot_speed - нужная скорость вращения этого вектора
        def make_lambda(i_func, rot_speed, zamedlenie):
            # вращение вокруг конца предыдущего вектора
            return lambda mobj, dt: mobj.rotate(dt * rot_speed * zamedlenie,
                                                about_point=Arrow_list[i_func - 1].get_end())

        # создаю список функций
        for i in range(quantity):
            if i == 0:
                # первая функция будет вращать первый вектор вокруг конца неподвижного нулевого вектора
                list_func.append(lambda mobj, dt: mobj.rotate(dt * zamedlenie,
                                                              about_point=[sdvig, 0, 0]))
            else:
                list_func.append(make_lambda(i + 1, list_rot_speed[i], zamedlenie))

        ######################################################################################################################################
        # 5. Рисую контур портрета. 5 - 7. Код создающий картинку.
        ######################################################################################################################################

        plane = NumberPlane()

        points = 2000

        t_points = np.linspace(0, 2 * np.pi, points)
        portrait_contour = [0 for i in range(points)]

        b = 0
        list_speed = [0]
        for i in range(quantity + 1):
            if i % 2 == 0:
                b += 1
            list_speed.append(b)
            b *= -1

        for j in range(points):
            for i in range(quantity + 1):
                portrait_contour[j] += list_c[i] * np.exp(-1j * list_speed[i] * t_points[j])

        line_graph = plane.plot_line_graph(
            x_values=[portrait_contour[i].real - 3 for i in range(len(portrait_contour))],
            y_values=[portrait_contour[i].imag for i in range(len(portrait_contour))],

            ###########################
            ###########################
            ###########################
            # - цвет убожество, нужен желтый с черным
            ###########################
            ###########################
            ###########################

            line_color='#D4FF00',
            stroke_width=1,
            vertex_dot_radius=0
        )

        # двигаю контур вправо. строчка обязательна
        # line_graph.move_to([sdvig, 0, 0])

        # рисую контур портрета
        self.wait(0.3)
        if choice_1 == 1:
            self.add(line_graph)

        ######################################################################################################################################
        # 6. Рисую вектора и трассировку конца последнего вектора
        ######################################################################################################################################
        self.wait(0.3)
        for i in range(quantity):
            if i == 0:
                # задержка перед появлением пнулевого вектора
                if choice == 1:
                    self.wait(0.3)
            else:
                # задержка перед появлением остальных векторов - постепенно уменьшается
                if choice == 1:
                    self.wait(1 / (i + 2))
            # отрисовка вектора. i+1, потому что нулевой вектор не рисуется
            if choice_3 == 1:
                self.add(Arrow_list[i + 1])

        # создаю трассировку конца последнего вектора желтым цветом
        self.add(TracedPath(Arrow_list[-1].get_end,
                            stroke_opacity=[40, 0],
                            # stroke_color='#33cc33',
                            stroke_color='#ffffdd',
                            stroke_width=0.2))

        ######################################################################################################################################
        # 7. Создаю зум
        ######################################################################################################################################

        frame = self.zoomed_camera.frame

        # двигаю зум на конец последнего вектора
        frame.move_to(Arrow_list[-1].get_end())

        # анимация появления зума
        self.activate_zooming(animate=True)

        ######################################################################################################################################
        # 8. Добавляю вращение
        ######################################################################################################################################

        # вращение векторов. нулевой вектор не вращается
        for i in range(quantity):
            if choice_3 == 1:
                Arrow_list[i + 1].add_updater(list_func[0])
            for j in range(i):
                if choice_3 == 1:
                    Arrow_list[i + 1].add_updater(list_func[j + 1])

        # вращение зума
        if choice_3 == 1:
            for j in range(quantity):
                frame.add_updater(list_func[j])

        # стабилизация зума
        if choice_3 == 1:
            frame.add_updater(lambda mobj, dt: mobj.rotate(dt * quantity / 2 * zamedlenie,
                                                           about_point=Arrow_list[len(Arrow_list) - 1].get_end()))

        # длина основной анимации
        self.wait(len_of_main_animation)
