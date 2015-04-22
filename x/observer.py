from x import signals


class BaseObserver(object):
    type_ = None

    def __init__(self, attached_to, name, value):
        """
        :param attached_to: resource.Resource
        :param name:
        :param value:
        :return:
        """
        self.attached_to = attached_to
        self.name = name
        self.value = value
        self.receivers = []

    def log(self, msg):
        print '{} {}'.format(self, msg)

    def __repr__(self):
        return '[{}:{}]'.format(self.attached_to.name, self.name)

    def __eq__(self, other):
        if isinstance(other, BaseObserver):
            return self.value == other.value

        return self.value == other

    def notify(self, emitter):
        """
        :param emitter: Observer
        :return:
        """
        raise NotImplementedError

    def update(self, value):
        """
        :param value:
        :return:
        """
        raise NotImplementedError

    def find_receiver(self, receiver):
        fltr = [r for r in self.receivers
                if r.attached_to == receiver.attached_to
                and r.name == receiver.name]
        if fltr:
            return fltr[0]

    def subscribe(self, receiver):
        """
        :param receiver: Observer
        :return:
        """
        self.log('Subscribe {}'.format(receiver))
        # No multiple subscriptions
        if self.find_receiver(receiver):
            self.log('No multiple subscriptions from {}'.format(receiver))
            return
        self.receivers.append(receiver)
        receiver.subscribed(self)

        signals.Connections.add(
            self.attached_to,
            self.name,
            receiver.attached_to,
            receiver.name
        )

        receiver.notify(self)

    def subscribed(self, emitter):
        self.log('Subscribed {}'.format(emitter))

    def unsubscribe(self, receiver):
        """
        :param receiver: Observer
        :return:
        """
        self.log('Unsubscribe {}'.format(receiver))
        if self.find_receiver(receiver):
            self.receivers.remove(receiver)
            receiver.unsubscribed(self)
        # TODO: ?
        #receiver.notify(self)

    def unsubscribed(self, emitter):
        self.log('Unsubscribed {}'.format(emitter))


class Observer(BaseObserver):
    type_ = 'simple'

    def __init__(self, *args, **kwargs):
        super(Observer, self).__init__(*args, **kwargs)
        # TODO:
        # Simple observer can be attached to at most one emitter
        self.emitter = None

    def notify(self, emitter):
        self.log('Notify from {} value {}'.format(emitter, emitter.value))
        # Copy emitter's values to receiver
        self.value = emitter.value
        for receiver in self.receivers:
            receiver.notify(self)
        self.attached_to.save()

    def update(self, value):
        self.log('Updating to value {}'.format(value))
        self.value = value
        for receiver in self.receivers:
            receiver.notify(self)
        self.attached_to.save()

    def subscribe(self, receiver):
        # TODO:
        super(Observer, self).subscribe(receiver)


class ListObserver(BaseObserver):
    type_ = 'list'

    def notify(self, emitter):
        self.log('Notify from {} value {}'.format(emitter, emitter.value))
        # Copy emitter's values to receiver
        self.value[emitter.attached_to.name] = emitter.value
        for receiver in self.receivers:
            receiver.notify(self)
        self.attached_to.save()

    def unsubscribed(self, emitter):
        """
        :param receiver: Observer
        :return:
        """
        self.log('Unsubscribed emitter {}'.format(emitter))
        self.value.pop(emitter.attached_to.name)


def create(type_, *args, **kwargs):
    for klass in BaseObserver.__subclasses__():
        if klass.type_ == type_:
            return klass(*args, **kwargs)
    raise NotImplementedError('No handling class for type {}'.format(type_))
