from abc import ABC, abstractmethod
from threading import Thread
import time
from typing import List, Union, Tuple, Callable, Any

from core import GameObject


class AbstractAnimation(ABC):

    def __init__(self, tick_ms=None):
        if tick_ms is not None:
            self.tick = tick_ms / 1000
        else:
            self.tick = None
        self.thread = None
        self._running = False

    def __repr__(self):
        return f'<Animation {id(self)}>'

    @abstractmethod
    def update(self):
        pass

    def _thread(self):
        while self.update() and self._running:
            if self.tick:
                time.sleep(self.tick)

    def run_in_thread(self):
        t = Thread(target=self._thread)
        self._running = True
        t.start()
        self.thread = t

    def stop_thread(self):
        self._running = False


class PropertyAnimation(AbstractAnimation):
    def __init__(
        self,
        obj: Any,
        propetry: str,
        anim_function: Callable[Any, float],
        tick_ms=None
    ):
        super().__init__(tick_ms)
        self.obj = obj
        self.propetry = propetry
        self.anim_function = anim_function
        self.time = time.perf_counter()

    def update(self):
        t = time.perf_counter()
        self.time, dt = t, t - self.time
        setattr(self.obj, self.propetry, anim_function(getattr(self.obj, self.propetry), dt))


class FuncAnimation(AbstractAnimation):
    def __init__(self, obj: Any, anim_function: Callable[Any, float], tick_ms=None):
        super().__init__(tick_ms)
        self.obj = obj
        self.anim_function = anim_function
        self.time = time.perf_counter()

    def update(self):
        t = time.perf_counter()
        self.time, dt = t, t - self.time
        anim_function(self.obj, dt)


class AnimationChain(AbstractAnimation):
    def __init__(self, animations: List[AbstractAnimation], tick_ms=None):
        super().__init__(tick_ms)
        self._animations = animations

    def update(self):
        for anim in self._animations[:]:
            if not anim.update():
                self.remove_animation(anim)

    def add_animation(self, animation: AbstractAnimation):
        if isinstance(animation, AbstractAnimation):
            self._animations.append(animation)
        else:
            raise TypeError(f'attempt to add object {animation}, that is not Animation')

    def remove_animation(self, animation: AbstractAnimation):
        try:
            self._animations.remove(animation)
        except KeyError:
            raise ValueError(
                'attempt to remove animation that is not in the list: '
                f'{Animation}'
            )


# ---- Old ----- #

class Animation:
    accepted_types = ['move']

    def __init__(self, obj, anim_type, duration, **params):
        # TODO избавиться от объекта, перерасчитывать только параметры
        self._obj = obj
        self._obj_x = obj.x
        self._obj_y = obj.y
        self._start_time = time.perf_counter()
        if anim_type not in self.accepted_types:
            raise ValueError(f'unknown animation type: {anim_type}')
        self.type = anim_type
        self._params = params
        self.duration = duration

    def __repr__(self):
        return f'<Animation({self.type}) {id(self)}>'

    def update(self):
        dt = (time.perf_counter() - self._start_time) / self.duration
        if dt > 1:
            return False
        if self.type == 'move':
            # TODO сделать более универсальным
            self._obj.x = self._obj_x + self._params['dx'] * dt
            self._obj.y = self._obj_y + self._params['dy'] * dt
        return True

    def parse_script(self):
        pass

    @classmethod
    def move(cls, obj, dx, dy, duration):
        return cls(obj, anim_type='move', duration=duration, dx=dx, dy=dy)


class Animated(GameObject):
    _animations: List[Animation]

    def __init__(self, animations: Union[List[Animation], Animation, None] = None, **params):
        super().__init__(**params)
        if animations is None:
            self._animations = []
        elif isinstance(animations, Animation):
            self._animations = [animations]
        elif isinstance(animations, list):
            if all(isinstance(x, Animation) for x in animations):
                self._animations = animations
            else:
                for a in animations:
                    if not isinstance(a, Animation):
                        raise TypeError(
                            f'only instance of Animation should be provided, got {a.__class__.__name__} instead.'
                        )
        else:
            raise TypeError(f'Animation or list of Animations should be provided, not {animations.__class__.__name__}')

    def update(self):
        for anim in self._animations[:]:
            if not anim.update():
                self.remove_animation(anim)

    def draw(self):
        pass

    def add_animation(self, animation: Animation):
        self._animations.append(animation)

    def remove_animation(self, animation: Animation):
        try:
            self._animations.remove(animation)
        except KeyError:
            raise ValueError(
                'attempt to remove animation that is not in the list: '
                f'{Animation}'
            )

    def move(self, dx, dy, duration):
        if hasattr(self, 'x') and hasattr(self, 'y'):
            self.add_animation(Animation.move(self, dx, dy, duration))
        else:
            raise TypeError(f'cannot move object {self} without x and y attributes')

    def stop(self):
        for anim in self._animations:
            if anim.type == 'move':
                self.remove_animation(anim)
